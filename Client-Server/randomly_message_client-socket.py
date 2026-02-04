import socket
import random
import string
import time

# --- Client Configuration ---
SERVER_IP = "172.23.198.195"  # Target Server IP
SERVER_PORT = 12000

def generate_random_string(length=10):
    """Generates a random string of lowercase ASCII characters."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

# 1. Determine the number of test messages (randomly between 5 and 15)
num_messages = random.randint(5, 15)
print("--- Starting Automated Test ---")
print(f"Target: {num_messages} messages will be sent.\n")

for i in range(num_messages):
    # 2. Generate random message payload
    message_content = generate_random_string(random.randint(5, 20))

    # 3. Create Socket
    # Note: The socket is initialized inside the loop because the server 
    # closes the connection after every single request (non-persistent).
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))

        # Send data
        print(f"[Msg {i+1}/{num_messages}] Sending: {message_content}")
        client_socket.send(message_content.encode())

        # Receive response
        modified_sentence = client_socket.recv(1024)
        print(f"   Server Response: {modified_sentence.decode()}")

    except Exception as e:
        print(f"Error on message {i+1}: {e}")

    finally:
        # Close the current connection
        client_socket.close()

    # Short delay to maintain readable output logs
    time.sleep(0.5)

print("\n--- Test Completed ---")
