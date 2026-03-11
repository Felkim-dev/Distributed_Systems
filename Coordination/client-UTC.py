import zmq
import threading
import time
import sys

hostname = "localhost"
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

def utc_time_client():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  # REQ stands for Request
    socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5s receive timeout

    try:
        socket.connect("tcp://" + hostname + ":" + port)  # Connect to the server's port

        # Send a request for UTC time
        socket.send_string("Time request")

        # Receive the UTC time from the server
        utc_time = socket.recv().decode('utf-8')
        print(f"Received UTC time: {utc_time}")
    except zmq.Again:
        print("Error: Server did not respond (timeout).")
    except zmq.ZMQError as e:
        print(f"ZMQ error: {e}")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    if not validate_port(port):
        sys.exit(1)

    c = [ ]
    for ii in range(3):
        c.append(threading.Thread(target=utc_time_client, args=()))
        c[ii].start()
        time.sleep(2)
        c[ii].join()
    print('Done')
    