import zmq, time, pickle, sys

def main():
    if len(sys.argv) < 2:
        print("$ python worker.py <WORKER_ID>")
        return

    context = zmq.Context()
    me = str(sys.argv[1])

    # PULL to receive tasks from the Broker
    r = context.socket(zmq.PULL)
    
    # Connect to the Brocker (Backend)
    HOST = 'localhost'
    PORT = '5558'
    p = "tcp://" + HOST + ":" + PORT
    
    print(f"Worker {me} connecting to {p}...")
    r.connect(p)

    count = 0
    while True:
        try:
            # We received the serialized message
            msg = r.recv()
            source_id, workload = pickle.loads(msg)
            
            count += 1
            print(f"Worker {me}: Received from Source {source_id} | load: {workload} | Tasks completed: {count}")
            
            # We simulate work
            time.sleep(workload * 0.01)
        except KeyboardInterrupt:
            break
            
    print(f"Worker {me} stopped.")

if __name__ == "__main__":
    main()
