import zmq
import time
import sys

port = "5000"

def validate_port(p):
    try:
        p_int = int(p)
        if not (1024 <= p_int <= 65535):
            raise ValueError
        return True
    except ValueError:
        print(f"Invalid port: {p}. Must be an integer between 1024 and 65535.")
        return False

def utc_time_server():
    if not validate_port(port):
        sys.exit(1)

    context = zmq.Context()
    socket = context.socket(zmq.REP)  	# REP stands for Reply

    try:
        socket.bind("tcp://*:" + port)  	# Bind to port 5000
    except zmq.ZMQError as e:
        print(f"Failed to bind to port {port}: {e}")
        socket.close()
        context.term()
        sys.exit(1)

    print("UTC Time Server running...")

    try:
        while True:
            # Wait for next request from client
            message = socket.recv()
            print(f"Received request: {message.decode()}")

            # Get UTC time
            utc_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

            # Send UTC time back to client
            socket.send_string(utc_time)
            print(f"Sent UTC time: {utc_time}")
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    except zmq.ZMQError as e:
        print(f"ZMQ error: {e}")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    utc_time_server()

