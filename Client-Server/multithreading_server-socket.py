from socket import *
import time
import threading

def handle_client(connection_socket, addr):
    """
    Handles the lifecycle of a single client connection 
    within a dedicated thread.
    """
    try:
        print(f"--> Thread started for: {addr}")

        # Receive incoming data
        data = connection_socket.recv(1024).decode()

        # Handle potential empty payloads or sudden disconnections
        if not data:
            print(f"Client {addr} closed the connection.")
            return

        print(f"Message received from {addr}: {data}")

        # Process the data (Convert to uppercase)
        processed_data = data.upper()

        # Simulate a blocking I/O operation or heavy processing
        time.sleep(3)

        # Send response back to client
        connection_socket.send(processed_data.encode())
        print(f"<-- Response sent to {addr}")

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        # Ensure the socket is closed regardless of success or failure
        connection_socket.close()

# --- Server Configuration ---
SERVER_PORT = 12000
server_socket = socket(AF_INET, SOCK_STREAM)

# Allow immediate reuse of the port after shutdown
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server_socket.bind(("", SERVER_PORT))

# Set backlog for queued connections
server_socket.listen(5)
print(f"Server is listening on port {SERVER_PORT} (Multithreaded Mode)")

while True:
    # Accept incoming connection requests
    connection_socket, addr = server_socket.accept()

    # Delegate client processing to a new thread
    # This prevents the main loop from blocking
    client_thread = threading.Thread(
        target=handle_client, 
        args=(connection_socket, addr)
    )

    # Start thread execution and immediately return to listen for new connections
    client_thread.start()
