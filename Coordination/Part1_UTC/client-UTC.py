import zmq
import threading
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
    parser = argparse.ArgumentParser(description="UTC Time Client using ZMQ")
    parser.add_argument(
        "-H",
        "--hostname",
        type=str,
        default="localhost",
        help="Server hostname or IP (default: localhost)",
    )
    parser.add_argument(
        "-p", "--port", type=str, default="5000", help="Server port (default: 5000)"
    )
    parser.add_argument(
        "-n",
        "--requests",
        type=int,
        default=3,
        help="Number of time requests to send (default: 3)",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=2.0,
        help="Delay in seconds between requests (default: 2.0)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=5000,
        help="Receive timeout in milliseconds (default: 5000)",
    )
    return parser.parse_args()


def utc_time_client(hostname, port, timeout):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  # REQ stands for Request
    socket.setsockopt(zmq.RCVTIMEO, timeout)

    try:
        socket.connect(f"tcp://{hostname}:{port}")

        # Send a request for UTC time
        socket.send_string("Time request")

        # Receive the UTC time from the server
        utc_time = socket.recv().decode("utf-8")
        print(f"Received UTC time: {utc_time}")
    except zmq.Again:
        print("Error: Server did not respond (timeout).")
    except zmq.ZMQError as e:
        print(f"ZMQ error: {e}")
    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    args = parse_args()

    if not validate_port(args.port):
        sys.exit(1)

    c = []
    for ii in range(args.requests):
        c.append(
            threading.Thread(
                target=utc_time_client, args=(args.hostname, args.port, args.timeout)
            )
        )
        c[ii].start()
        time.sleep(args.delay)
        c[ii].join()
    print("Done")
