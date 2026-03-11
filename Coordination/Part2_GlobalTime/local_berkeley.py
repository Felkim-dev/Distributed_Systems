import zmq
import threading
import time
import random
import argparse
import sys
from datetime import datetime


# Argument parsing  (no required args – everything has a sensible default)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Berkeley Clock Sync – launch N peer nodes on one machine"
    )
    parser.add_argument("-n", "--nodes", type=int, default=3,
                        help="Number of peer nodes (default: 3)")
    parser.add_argument("--base-port", type=int, default=5000,
                        help="First port; nodes use base, base+1, … (default: 5000)")
    parser.add_argument("-k", "--drift-every", type=int, default=3,
                        help="Inject random drift every k sync cycles (default: 3)")
    parser.add_argument("--drift-max", type=float, default=5.0,
                        help="Max random drift in seconds (default: 5.0)")
    parser.add_argument("--sync-interval", type=float, default=4.0,
                        help="Seconds between sync rounds (default: 4.0)")
    parser.add_argument("--rounds", type=int, default=10,
                        help="Sync rounds per node (default: 10)")
    parser.add_argument("--timeout", type=int, default=2000,
                        help="Per-peer receive timeout in ms (default: 2000)")
    parser.add_argument("--initial-drift-max", type=float, default=10.0,
                        help="Max initial random clock offset at startup (default: 10.0)")
    return parser.parse_args()


# PeerNode Class

class PeerNode:
    def __init__(self, node_id, port, peers,
                 drift_every=3, drift_max=5.0,
                 sync_interval=4.0, rounds=10, timeout=2000):
        self.node_id       = node_id
        self.port          = port
        self.peers         = peers
        self.drift_every   = drift_every
        self.drift_max     = drift_max
        self.sync_interval = sync_interval
        self.rounds        = rounds
        self.timeout       = timeout
        self._offset      = 0.0
        self._offset_lock = threading.Lock()
        self._stop_event  = threading.Event()
        self._cycle       = 0

    def local_time(self):
        with self._offset_lock:
            return time.time() + self._offset

    def adjust_clock(self, delta):
        with self._offset_lock:
            self._offset += delta

    def inject_drift(self):
        drift = random.uniform(-self.drift_max, self.drift_max)
        with self._offset_lock:
            self._offset += drift
        self._log(f" Drift injected: {drift:+.3f}s  (total offset = {self._offset:+.3f}s)")

    def _log(self, msg):
        wall     = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
        local_ts = datetime.utcfromtimestamp(self.local_time()).strftime("%H:%M:%S.%f")[:-3]
        print(f"[{wall} UTC | {self.node_id} local={local_ts}] {msg}", flush=True)

    def _server_thread(self):
        ctx    = zmq.Context()
        socket = ctx.socket(zmq.REP)
        try:
            socket.bind(f"tcp://*:{self.port}")
        except zmq.ZMQError as e:
            print(f"[{self.node_id}] Cannot bind port {self.port}: {e}", flush=True)
            ctx.term()
            return
        socket.setsockopt(zmq.RCVTIMEO, 500)
        self._log(f"Server listening on port {self.port}")
        while not self._stop_event.is_set():
            try:
                socket.recv_string()
                socket.send_string(f"{self.local_time():.6f}")
            except zmq.Again:
                continue
            except zmq.ZMQError as e:
                self._log(f"Server ZMQ error: {e}")
                break
        socket.close()
        ctx.term()

    def _query_peer(self, peer_addr, results, index):
        ctx    = zmq.Context()
        socket = ctx.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        socket.setsockopt(zmq.LINGER, 0)
        try:
            socket.connect(f"tcp://{peer_addr}")
            t_send    = self.local_time()
            socket.send_string("TIME_REQUEST")
            peer_time = float(socket.recv_string())
            rtt       = self.local_time() - t_send
            results[index] = peer_time + rtt / 2.0
        except zmq.Again:
            self._log(f" Timeout from {peer_addr}")
            results[index] = None
        except Exception as e:
            self._log(f" Error querying {peer_addr}: {e}")
            results[index] = None
        finally:
            socket.close()
            ctx.term()

    def _sync_round(self):
        self._cycle += 1
        self._log(f"── Sync round {self._cycle} {'─'*40}")
        if self._cycle % self.drift_every == 0:
            self.inject_drift()
        my_time = self.local_time()
        if not self.peers:
            self._log("No peers – skipping sync.")
            return
        results = [None] * len(self.peers)
        threads = [threading.Thread(target=self._query_peer,
                                    args=(peer, results, i), daemon=True)
                   for i, peer in enumerate(self.peers)]
        for t in threads: t.start()
        for t in threads: t.join()

        valid_times = [my_time]
        for i, peer in enumerate(self.peers):
            if results[i] is not None:
                self._log(f"  Peer {peer}  diff={results[i]-my_time:+.3f}s")
                valid_times.append(results[i])
            else:
                self._log(f"  Peer {peer}  → no response")

        mean_time = sum(valid_times) / len(valid_times)
        delta     = mean_time - my_time
        self._log(f"  Nodes used={len(valid_times)}  mean={mean_time:.3f}  "
                  f"mine={my_time:.3f}  adj={delta:+.2f}s")
        self.adjust_clock(delta)
        self._log(f" New offset = {self._offset:+.2f}s")

    def run(self):
        srv = threading.Thread(target=self._server_thread, daemon=True)
        srv.start()
        time.sleep(0.5)
        self._log(f"Starting {self.rounds} sync rounds "
                  f"(drift every {self.drift_every} cycles, interval={self.sync_interval}s)")
        for _ in range(self.rounds):
            self._sync_round()
            time.sleep(self.sync_interval)
        self._log("All rounds complete.")
        self._stop_event.set()
        srv.join(timeout=2)



def main():
    args = parse_args()

    print("=" * 70)
    print("  Berkeley Clock Synchronization – Multi-Node Simulation")
    print("=" * 70)
    print(f"  Nodes          : {args.nodes}")
    print(f"  Base port      : {args.base_port} – {args.base_port + args.nodes - 1}")
    print(f"  Sync interval  : {args.sync_interval}s  |  Rounds: {args.rounds}")
    print(f"  Drift every k  : {args.drift_every} cycles  |  Max: ±{args.drift_max}s")
    print(f"  Initial drift  : ±{args.initial_drift_max}s")
    print("=" * 70)

    ports = [str(args.base_port + i) for i in range(args.nodes)]
    nodes = []
    for i in range(args.nodes):
        port  = ports[i]
        peers = [f"localhost:{ports[j]}" for j in range(args.nodes) if j != i]
        node  = PeerNode(
            node_id=f"Node{i+1}", port=port, peers=peers,
            drift_every=args.drift_every, drift_max=args.drift_max,
            sync_interval=args.sync_interval, rounds=args.rounds,
            timeout=args.timeout,
        )
        node._offset = random.uniform(-args.initial_drift_max, args.initial_drift_max)
        print(f"  Node{i+1:1d}  port={port}  initial_offset={node._offset:+.2f}s  peers={peers}")
        nodes.append(node)

    print("=" * 70)

    threads = []
    for node in nodes:
        t = threading.Thread(target=node.run, name=node.node_id, daemon=True)
        threads.append(t)
        t.start()
        time.sleep(0.2)

    for t in threads:
        t.join()

    print("=" * 70)
    print("Simulation complete. Final offsets vs wall clock:")
    for node in nodes:
        print(f"  {node.node_id:10s}  offset = {node._offset:+.2f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()
