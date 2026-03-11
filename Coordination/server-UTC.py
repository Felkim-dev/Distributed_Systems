import zmq
import time
import sys
import argparse


def validate_port(p):
    try:
        p_int = int(p)
        if not (1024 <= p_int <= 65535):
            raise ValueError
        return True
    except ValueError:
        print(f"Invalid port: {p}. Must be an integer between 1024 and 65535.")
        return False


def parse_args():
    parser = argparse.ArgumentParser(description="UTC Time Server using ZMQ")
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default="5000",
        help="Port to bind the server (default: 5000)",
    )
    parser.add_argument(
        "-b",
        "--bind",
        type=str,
        default="*",
        help="Address to bind (default: * = all interfaces)",
    )
    return parser.parse_args()


def utc_time_server(bind_address, port):
    if not validate_port(port):
        sys.exit(1)

    context = zmq.Context()
    socket = context.socket(zmq.REP)  # REP stands for Reply

    try:
        socket.bind(f"tcp://{bind_address}:{port}")
    except zmq.ZMQError as e:
        print(f"Failed to bind to {bind_address}:{port}: {e}")
        socket.close()
        context.term()
        sys.exit(1)

    print(f"UTC Time Server running on {bind_address}:{port}...")

    try:
        while True:
            # Wait for next request from client
            message = socket.recv()
            print(f"Received request: {message.decode()}")

            # Get UTC time
            utc_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

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
    args = parse_args()
    utc_time_server(args.bind, args.port)
