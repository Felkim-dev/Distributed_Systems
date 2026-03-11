# Implement the Central Resource Management Server (Centralized Approach)

## file: server.py using ZeroMQ (ZMQ).

The server act as the central coordinator. It listen for REQUEST messages from clients, maintain a queue of requests, send a GRANT message to the first client in the queue, and wait for a RELEASE message before granting access to the next client in line.


## file: client.py using ZMQ and threading.

The client simulate a process that needs to access a shared resource. It will send a REQUEST to the server, wait for the GRANT message, simulate using the resource (e.g., printing a timestamp and sleeping for a few seconds), and finally send a RELEASE message back to the server.
