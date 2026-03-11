import zmq
import threading
import time
import random
import argparse
import sys
from datetime import datetime

#FUNCIONES DE VALIDACION

def validate_port(p):
    try:
        p_int = int(p)
        if not (1024 <= p_int <= 65535):
            raise ValueError
        return True
    except ValueError:
        print(f"[ERROR] Invalid port: {p}. Must be an integer between 1024 and 65535.")
        return False

def parse_args():
    parser = argparse.ArgumentParser(
        description="Berkeley Clock Sync – single peer node"
    )
    parser.add_argument(
        "-i", "--id",
        type=str, required=True,
        help="Unique name/ID for this node (e.g. Node1)"
    )
    parser.add_argument(
        "-p", "--port",
        type=str, required=True,
        help="Port this node listens on"
    )
    parser.add_argument(
        "--peers",
        type=str, nargs="+", default=[],
        metavar="HOST:PORT",
        help="List of peer addresses, e.g. localhost:5001 localhost:5002"
    )
    parser.add_argument(
        "-k", "--drift-every",
        type=int, default=3,
        help="Inject random drift every k sync cycles (default: 3)"
    )
    parser.add_argument(
        "--drift-max",
        type=float, default=5.0,
        help="Maximum random drift in seconds (default: 5.0)"
    )
    parser.add_argument(
        "--sync-interval",
        type=float, default=4.0,
        help="Seconds between synchronisation rounds (default: 4.0)"
    )
    parser.add_argument(
        "--rounds",
        type=int, default=10,
        help="Number of synchronisation rounds before stopping (default: 10)"
    )
    parser.add_argument(
        "--timeout",
        type=int, default=2000,
        help="Per-peer receive timeout in ms (default: 2000)"
    )
    return parser.parse_args()

#Node class

class PeerNode:
    
    def __init__(self,node_id, port, peers,
                 drift_every=3, drift_max=5.0,
                 sync_interval=4.0, rounds=10,timeout=2000):
        self.node_id       = node_id
        self.port          = port
        self.peers         = peers          # list of "host:port" strings
        self.drift_every   = drift_every
        self.drift_max     = drift_max
        self.sync_interval = sync_interval
        self.rounds        = rounds
        self.timeout       = timeout

        self._offset       = 0.0           # simulated clock offset (seconds)
        self._offset_lock  = threading.Lock()
        self._stop_event   = threading.Event()
        self._cycle        = 0             # sync cycle counter

    def local_time(self):
        #devuelve la hora local simulada (float,unix, seconds)
        with self._offset_lock:
            return time.time() + self._offset
    
    def adjust_clock(self, delta):
        #suma un delta al desfase
        with self._offset_lock:
            self._offset+= delta

    def inject_drift(self):
        #agrega una deriva aleatoria para simular el desfase del reloj
        drift=random.uniform(-self.drift_max,self.drift_max)
        with self._offset_lock:
            self._offset+= drift
        self._log(f"Drift injected: {drift:+.2f}s "
                  f"total offset now {self._offset:+.2f})s")
    def _log(self, msg):
        #para mostrar la transaccion en la consola
        wall=datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
        local_ts=datetime.utcfromtimestamp(self.local_time()).strftime(
           "%H:%M:%S.%f")[:-3]
        print(f"[{wall} UTC | {self.node_id} local={local_ts}] {msg}",
              flush=True)
    
#zmq server thread
    def _server_thread(self):
        """Listen for time-request messages and reply with local time."""
        ctx    = zmq.Context()
        socket = ctx.socket(zmq.REP)
        try:
            socket.bind(f"tcp://*:{self.port}")
        except zmq.ZMQError as e:
            print(f"[{self.node_id}] Cannot bind port {self.port}: {e}")
            ctx.term()
            return

        socket.setsockopt(zmq.RCVTIMEO, 500)   # 500 ms poll so we can check stop

        self._log(f"Server listening on port {self.port}")
        while not self._stop_event.is_set():
            try:
                msg = socket.recv_string()
                if msg == "TIME_REQUEST":
                    t = self.local_time()
                    socket.send_string(f"{t:.6f}")
                else:
                    socket.send_string("UNKNOWN")
            except zmq.Again:
                continue    # timeout → loop & check stop_event
            except zmq.ZMQError as e:
                self._log(f"Server ZMQ error: {e}")
                break

        socket.close()
        ctx.term() 

    def _query_peer(self, peer_addr, results, index):
        """
        Ask a single peer for its current time.
        results[index] is set to the peer's reported time (float) or None.
        """
        ctx    = zmq.Context()
        socket = ctx.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        socket.setsockopt(zmq.LINGER, 0)
        try:
            socket.connect(f"tcp://{peer_addr}")
            t_send = self.local_time()
            socket.send_string("TIME_REQUEST")
            reply  = socket.recv_string()
            t_recv = self.local_time()
            peer_time = float(reply)
            # Compensate for round-trip: estimate peer clock at midpoint
            rtt   = t_recv - t_send
            results[index] = peer_time + rtt / 2.0
        except zmq.Again:
            self._log(f" Timeout waiting for {peer_addr}")
            results[index] = None
        except Exception as e:
            self._log(f" Error querying {peer_addr}: {e}")
            results[index] = None
        finally:
            socket.close()
            ctx.term()
    def _sync_round(self):
        """
        Berkeley-style sync:
          1. Query all peers in parallel.
          2. Collect valid responses + own time.
          3. Compute mean time.
          4. Adjust own clock by (mean - local).
        """
        self._cycle += 1
        self._log(f"── Sync round {self._cycle} ──────────────────────")

        # Possibly inject drift
        if self._cycle % self.drift_every == 0:
            self.inject_drift()

        my_time = self.local_time()

        if not self.peers:
            self._log("No peers configured – skipping sync.")
            return

        # Query peers in parallel
        results  = [None] * len(self.peers)
        threads  = []
        for i, peer in enumerate(self.peers):
            t = threading.Thread(
                target=self._query_peer,
                args=(peer, results, i),
                daemon=True
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Gather valid times (include own)
        valid_times = [my_time]
        for i, peer in enumerate(self.peers):
            if results[i] is not None:
                valid_times.append(results[i])
                diff = results[i] - my_time
                self._log(f"  Peer {peer}: reported_time={results[i]:.2f}  "
                          f"diff={diff:+.2f}s")
            else:
                self._log(f"  Peer {peer}: no response")

        # Compute mean and adjust
        mean_time = sum(valid_times) / len(valid_times)
        delta     = mean_time - my_time

        self._log(f"  Responding nodes : {len(valid_times)}  "
                  f"(me + {len(valid_times)-1} peers)")
        self._log(f"  Mean time        : {mean_time:.2f}")
        self._log(f"  My time          : {my_time:.2f}")
        self._log(f"  Adjustment       : {delta:+.6f}s")

        self.adjust_clock(delta)
        self._log(f"  ✓ Clock adjusted. New offset = {self._offset:+.6f}s")

    def run(self):
        # Start server in background
        server = threading.Thread(target=self._server_thread, daemon=True)
        server.start()

        # Give server a moment to bind
        time.sleep(0.5)

        self._log(f"Starting {self.rounds} sync rounds "
                  f"(drift every {self.drift_every} cycles, "
                  f"interval={self.sync_interval}s)")

        for _ in range(self.rounds):
            self._sync_round()
            time.sleep(self.sync_interval)

        self._log("All rounds complete. Shutting down.")
        self._stop_event.set()
        server.join(timeout=2)


if __name__ == "__main__":
    args = parse_args()

    if not validate_port(args.port):
        sys.exit(1)

    node = PeerNode(
        node_id       = args.id,
        port          = args.port,
        peers         = args.peers,
        drift_every   = args.drift_every,
        drift_max     = args.drift_max,
        sync_interval = args.sync_interval,
        rounds        = args.rounds,
        timeout       = args.timeout,
    )
    node.run()
