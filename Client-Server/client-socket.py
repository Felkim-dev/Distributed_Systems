import socket

# --- Client Configuration ---
SERVER_IP = "172.23.198.227"
SERVER_PORT = 12000

keep_running = True

while keep_running:
    # Initialize socket (IPv4, TCP)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Set a 10-second timeout for blocking operations
    client_socket.settimeout(10)

    print(f"\nAttempting to connect to {SERVER_IP}:{SERVER_PORT}...")

    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print("Connection established.")
    except Exception as e:
        print(f"Connection failed: {e}")
        # Exit loop if connection is impossible
        break

    message = input("Enter lowercase sentence: ")

    try:
        client_socket.send(message.encode())

        # Wait for response
        response = client_socket.recv(1024)

        # Validate connection status
        if not response:
            print("Server closed the connection unexpectedly (empty response).")
            keep_running = False
        else:
            print(f"From Server: {response.decode()}")

    except socket.timeout:
        print("Error: Server request timed out.")
    except Exception as e:
        print(f"Communication error: {e}")

    # Prompt user to continue only if no fatal errors occurred
    if keep_running:
        user_choice = input("Send another message? (Y/N): ")
        if user_choice.strip().upper() == "N":
            keep_running = False

    # Ensure socket is closed before next iteration
    client_socket.close()
