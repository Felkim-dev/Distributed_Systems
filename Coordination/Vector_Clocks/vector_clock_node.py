"""
Networked Vector Clock Node
============================
Each node runs as a separate process (potentially on a different machine).
Nodes communicate via ZMQ PUSH/PULL sockets, piggybacking their vector clock
on every message — exactly as described by the vector clock algorithm.

Usage:
    python vector_clock_node.py --node-id Node_1 --port 5001 \
        --peers Node_2=localhost:5002 Node_3=localhost:5003

    python vector_clock_node.py --node-id Node_2 --port 5002 \
        --peers Node_1=localhost:5001 Node_3=localhost:5003

Interactive commands once running:
    tick              - Execute a local event (increments own clock)
    send <node_id>    - Send a message to a peer (increments clock + sends vector)
    state             - Print the current vector clock
    compare <node_id> - Compare your clock with the last received state of a peer
    peers             - List known peers and their addresses
    history           - Show the event log
    help              - Show available commands
    quit              - Exit the node
"""

import zmq
import json
import threading
import argparse
import sys
import time

from Vector_Clock import VectorClock, CausalityChecker


def parse_args():
    parser = argparse.ArgumentParser(
        description="Networked Vector Clock Node using ZMQ"
    )
    parser.add_argument(
        "--node-id",
        type=str,
        required=True,
        help="Unique identifier for this node (e.g. Node_1)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        required=True,
        help="Port this node listens on for incoming messages (PULL socket)",
    )
    parser.add_argument(
        "--bind",
        type=str,
        default="*",
        help="Address to bind the listener (default: * = all interfaces)",
    )
    parser.add_argument(
        "--peers",
        nargs="*",
        default=[],
        help="Peers in the format NodeId=host:port (e.g. Node_2=192.168.1.5:5002)",
    )
    return parser.parse_args()


def parse_peers(peer_list):
    """Parse peer strings like 'Node_2=localhost:5002' into a dict."""
    peers = {}
    for entry in peer_list:
        if "=" not in entry:
            print(
                f"  [WARNING] Ignoring malformed peer: {entry}  (expected format: NodeId=host:port)"
            )
            continue
        node_id, address = entry.split("=", 1)
        peers[node_id.strip()] = address.strip()
    return peers


class NetworkedVectorClockNode:
    """
    A distributed vector clock node that communicates over ZMQ.
    - PULL socket: receives messages from other nodes.
    - PUSH sockets: created on-demand to send messages to peers.
    """

    def __init__(self, node_id, bind_address, port, peers):
        self.vclock = VectorClock(node_id)
        self.node_id = node_id
        self.bind_address = bind_address
        self.port = port
        self.peers = peers  # {node_id: "host:port"}
        self.peer_last_state = {}  # Last vector received from each peer
        self.event_log = []  # Log of all events
        self.lock = threading.Lock()  # Protect shared state
        self.running = True

        # ZMQ context shared across threads
        self.context = zmq.Context()

        # Persistent PUSH sockets — one per peer, established at startup
        # so the TCP connection is ready when we need to send.
        self.push_sockets = {}
        for peer_id, address in self.peers.items():
            sock = self.context.socket(zmq.PUSH)
            sock.setsockopt(zmq.SNDTIMEO, 5000)  # 5s send timeout
            sock.setsockopt(zmq.LINGER, 2000)
            sock.connect(f"tcp://{address}")
            self.push_sockets[peer_id] = sock
            print(f"  [INIT] Connected PUSH socket to {peer_id} at {address}")

    def start_listener(self):
        """Background thread: listens for incoming messages on a PULL socket."""
        receiver = self.context.socket(zmq.PULL)
        receiver.bind(f"tcp://{self.bind_address}:{self.port}")

        poller = zmq.Poller()
        poller.register(receiver, zmq.POLLIN)

        while self.running:
            # Poll with a timeout so we can check self.running periodically
            socks = dict(poller.poll(timeout=1000))
            if receiver in socks:
                raw = receiver.recv_string()
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                sender_id = data.get("sender", "unknown")
                incoming_vector = data.get("vector", {})
                payload = data.get("message", "")

                with self.lock:
                    self.vclock.receive_event(incoming_vector)
                    self.peer_last_state[sender_id] = incoming_vector
                    state_snapshot = self.vclock.get_state().copy()
                    self.event_log.append(
                        {
                            "type": "receive",
                            "from": sender_id,
                            "incoming_vector": incoming_vector,
                            "state_after": state_snapshot,
                        }
                    )

                print(f'\n  << Received from {sender_id}: "{payload}"')
                print(f"     Incoming vector : {incoming_vector}")
                print(f"     Local clock now : {state_snapshot}")
                print(f"[{self.node_id}] > ", end="", flush=True)

        receiver.close()

    def send_to_peer(self, target_id, message="sync"):
        """Send a message to a specific peer, piggybacking the vector clock."""
        if target_id not in self.push_sockets:
            print(
                f"  [ERROR] Unknown peer: {target_id}. Use 'peers' to see known nodes."
            )
            return

        address = self.peers[target_id]
        sender = self.push_sockets[target_id]

        try:
            with self.lock:
                outgoing_vector = self.vclock.send_event()
                state_snapshot = self.vclock.get_state().copy()
                self.event_log.append(
                    {
                        "type": "send",
                        "to": target_id,
                        "vector_sent": outgoing_vector,
                        "state_after": state_snapshot,
                    }
                )

            payload = json.dumps(
                {"sender": self.node_id, "vector": outgoing_vector, "message": message}
            )
            sender.send_string(payload)
            print(f"  >> Sent to {target_id} ({address})")
            print(f"     Vector sent   : {outgoing_vector}")
            print(f"     Local clock   : {state_snapshot}")
        except zmq.Again:
            print(f"  [ERROR] Could not reach {target_id} at {address} (timeout).")
        except zmq.ZMQError as e:
            print(f"  [ERROR] ZMQ error sending to {target_id}: {e}")

    def local_tick(self):
        """Execute a local event (no network communication)."""
        with self.lock:
            self.vclock.tick()
            state_snapshot = self.vclock.get_state().copy()
            self.event_log.append({"type": "local_tick", "state_after": state_snapshot})
        print(f"  Local event executed.")
        print(f"  Clock: {state_snapshot}")

    def show_state(self):
        with self.lock:
            state = self.vclock.get_state().copy()
        print(f"  Current vector clock: {state}")

    def show_peers(self):
        if not self.peers:
            print("  No peers configured.")
            return
        print("  Known peers:")
        for nid, addr in self.peers.items():
            last = self.peer_last_state.get(nid, "never received")
            print(f"    {nid} -> {addr}  (last seen vector: {last})")

    def compare_with_peer(self, peer_id):
        with self.lock:
            my_state = self.vclock.get_state().copy()

        if peer_id not in self.peer_last_state:
            print(
                f"  No state received yet from {peer_id}. Send/receive a message first."
            )
            return

        peer_state = self.peer_last_state[peer_id]
        result = CausalityChecker.compare(my_state, peer_state)

        print(f"  My state (A)        : {my_state}")
        print(f"  {peer_id}'s last (B) : {peer_state}")
        print(f"  Relationship        : {result}")

    def show_history(self):
        if not self.event_log:
            print("  No events recorded yet.")
            return
        print("  Event history:")
        for i, event in enumerate(self.event_log, 1):
            etype = event["type"]
            state = event["state_after"]
            if etype == "local_tick":
                print(f"    {i}. [TICK]    -> {state}")
            elif etype == "send":
                print(
                    f"    {i}. [SEND]    to {event['to']} | sent: {event['vector_sent']} -> {state}"
                )
            elif etype == "receive":
                print(
                    f"    {i}. [RECEIVE] from {event['from']} | incoming: {event['incoming_vector']} -> {state}"
                )

    def show_help(self):
        print("  Available commands:")
        print("    tick                       - Execute a local event")
        print("    send <node_id> [message]   - Send a message to a peer")
        print("    state                      - Show the current vector clock")
        print("    compare <node_id>          - Compare clock with a peer's last state")
        print("    peers                      - List known peers")
        print("    history                    - Show event log")
        print("    help                       - Show this help")
        print("    quit                       - Exit")

    def run(self):
        """Start the listener thread and the interactive CLI."""
        listener_thread = threading.Thread(target=self.start_listener, daemon=True)
        listener_thread.start()

        print(f"  Node '{self.node_id}' listening on port {self.port}")
        print(f"  Peers: {self.peers if self.peers else 'none (add with --peers)'}")
        print(f"  Type 'help' for available commands.\n")

        try:
            while self.running:
                try:
                    raw_input = input(f"[{self.node_id}] > ").strip()
                except EOFError:
                    break

                if not raw_input:
                    continue

                parts = raw_input.split(maxsplit=2)
                cmd = parts[0].lower()

                if cmd == "quit":
                    self.running = False
                    print("  Shutting down...")
                elif cmd == "tick":
                    self.local_tick()
                elif cmd == "send":
                    if len(parts) < 2:
                        print("  Usage: send <node_id> [message]")
                        continue
                    target = parts[1]
                    message = parts[2] if len(parts) > 2 else "sync"
                    self.send_to_peer(target, message)
                elif cmd == "state":
                    self.show_state()
                elif cmd == "compare":
                    if len(parts) < 2:
                        print("  Usage: compare <node_id>")
                        continue
                    self.compare_with_peer(parts[1])
                elif cmd == "peers":
                    self.show_peers()
                elif cmd == "history":
                    self.show_history()
                elif cmd == "help":
                    self.show_help()
                else:
                    print(f"  Unknown command: '{cmd}'. Type 'help' for options.")
        except KeyboardInterrupt:
            self.running = False
            print("\n  Interrupted. Shutting down...")
        finally:
            # Close all persistent PUSH sockets
            for sock in self.push_sockets.values():
                sock.close()
            self.context.term()


if __name__ == "__main__":
    args = parse_args()

    if not (1024 <= args.port <= 65535):
        print(f"Invalid port: {args.port}. Must be between 1024 and 65535.")
        sys.exit(1)

    peers = parse_peers(args.peers)
    node = NetworkedVectorClockNode(args.node_id, args.bind, args.port, peers)
    node.run()
