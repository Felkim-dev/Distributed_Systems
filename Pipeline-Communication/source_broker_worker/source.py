import zmq, time, pickle, sys, random

def main():
    if len(sys.argv) < 2:
        print("$ python source.py <SOURCE_ID>")
        return

    context = zmq.Context()
    me = str(sys.argv[1])

    # PUSH tasks to the Broker
    s = context.socket(zmq.PUSH)

    # Connect to the Broker (Frontend)
    HOST = 'localhost'
    PORT = '5557'
    p = "tcp://" + HOST + ":" + PORT

    print(f"Source {me} connecting to {p}...")
    s.connect(p)

    # Send 10 tasks
    for i in range(10):
        workload = random.randint(1, 100)
        print(f"Source {me} sending task: {workload}")
        s.send(pickle.dumps((me, workload)))
        time.sleep(0.5)

    print(f"Source {me} finished sending.")

if __name__ == "__main__":
    main()
