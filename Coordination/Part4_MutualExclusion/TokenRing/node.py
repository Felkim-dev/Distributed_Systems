import zmq
import time
import random
import sys
import threading
import argparse

def main():
    parser = argparse.ArgumentParser(description="Token Ring Node")
    parser.add_argument("--id", required=True, help="Node identifier (e.g., A, B, C)")
    parser.add_argument("--bind", required=True, help="Port to bind and listen for the token")
    parser.add_argument("--connect", required=True, help="Port of the next node to send the token to")
    parser.add_argument("--initiator", action="store_true", help="Flag to indicate if this node starts the token")
    
    args = parser.parse_args()
    
    node_id = args.id
    my_port = args.bind
    next_port = args.connect
    is_initiator = args.initiator

    context = zmq.Context()
    
    # 1. Socket to RECEIVE from the previous node
    receiver = context.socket(zmq.PULL)
    receiver.bind(f"tcp://*:{my_port}")
    
    # 2. Socket to SEND to the next node
    sender = context.socket(zmq.PUSH)
    
    print(f"[{node_id}] Node initializing...")
    print(f"[{node_id}] Listening on port {my_port} | Forwarding to port {next_port}")
    
    # We add a slight delay before connecting to ensure the next node has time to bind
    time.sleep(2)
    sender.connect(f"tcp://localhost:{next_port}")
    
    # State variable for the shared resource
    wants_resource = False

    # 3. Background thread to randomly request the resource
    def request_generator():
        nonlocal wants_resource
        while True:
            # Wait for a random interval before needing the resource again
            time.sleep(random.uniform(5.0, 10.0))
            if not wants_resource:
                print(f"\n[{node_id}] >>> I need to access the shared resource! Waiting for token... <<<")
                wants_resource = True

    # Start the background thread
    threading.Thread(target=request_generator, daemon=True).start()

    # 4. If this is the initiator, inject the first token into the ring
    if is_initiator:
        print(f"[{node_id}] I am the initiator. Injecting the TOKEN into the ring in 3 seconds...")
        time.sleep(3)
        sender.send_string("TOKEN")

    # 5. Main Loop: Handle the Token
    while True:
        try:
            # Block until a message is received from the previous node
            message = receiver.recv_string()
            
            if message == "TOKEN":
                print(f"[{node_id}] Received TOKEN.")
                
                # Check if we need to access the critical section
                if wants_resource:
                    print(f"[{node_id}] *** ENTERING CRITICAL SECTION ***")
                    # Simulate time spent using the resource
                    time.sleep(random.uniform(2.0, 4.0)) 
                    print(f"[{node_id}] *** LEAVING CRITICAL SECTION ***")
                    # Done with the resource
                    wants_resource = False 
                else:
                    print(f"[{node_id}] Token received, but resource not needed.")
                
                # Small delay so the terminal output doesn't go too fast to read
                time.sleep(1) 
                
                print(f"[{node_id}] Passing TOKEN to the next node.\n")
                sender.send_string("TOKEN")
                
        except KeyboardInterrupt:
            print(f"\n[{node_id}] Shutting down node...")
            break

    # Clean up
    receiver.close()
    sender.close()
    context.term()

if __name__ == "__main__":
    main()
