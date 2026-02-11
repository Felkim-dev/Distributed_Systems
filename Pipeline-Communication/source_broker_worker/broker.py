import zmq

def main():
    context = zmq.Context()

    # Receives messages from Sources (PULL)
    frontend = context.socket(zmq.PULL)
    frontend.bind("tcp://*:5557")

    # Send messages to the Workers (PUSH)
    backend = context.socket(zmq.PUSH)
    backend.bind("tcp://*:5558")

    print("Broker started... (Ctrl+C to stop)")
    print("Listening to Sources on port 5557")
    print("Sending to Workers on port 5558")

    # Start the proxy that automatically moves data from frontend to backend
    try:
        zmq.proxy(frontend, backend)
    except KeyboardInterrupt:
        print("Broker stopped.")
    finally:
        frontend.close()
        backend.close()
        context.term()

if __name__ == "__main__":
    main()
