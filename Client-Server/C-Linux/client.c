#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 12000
#define BUFFER_SIZE 1024
#define SERVER_IP "172.23.198.195"

int main() {
    int sock;
    struct sockaddr_in server_addr;
    char message[BUFFER_SIZE];
    char server_reply[BUFFER_SIZE];
    char user_choice[10];
    int run_loop = 1;

    while (run_loop) {
        // 1. Initialize socket
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock == -1) {
            perror("Socket creation failed");
            return 1;
        }

        // Configure server address structure
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(PORT);
        server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);

        printf("\nConnecting to %s:%d...\n", SERVER_IP, PORT);

        // 2. Establish connection
        if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            perror("Connection failed");
            close(sock);
            break;
        }
        printf("Connected successfully.\n");

        // 3. User input
        printf("Enter lowercase sentence: ");
        if (fgets(message, BUFFER_SIZE, stdin) != NULL) {
            // Remove newline character
            message[strcspn(message, "\n")] = 0;
        }

        // 4. Send data to server
        if (send(sock, message, strlen(message), 0) < 0) {
            perror("Send failed");
            close(sock);
            break;
        }

        // 5. Receive server response
        ssize_t received_bytes = recv(sock, server_reply, BUFFER_SIZE - 1, 0);
        if (received_bytes < 0) {
            perror("Receive failed");
        } else if (received_bytes == 0) {
            printf("Server closed the connection.\n");
        } else {
            server_reply[received_bytes] = '\0'; 
            printf("From Server: %s\n", server_reply);
        }

        // 6. Close socket for current transaction
        close(sock);

        // Prompt for continuation
        printf("Send another message? (y/n): ");
        if (fgets(user_choice, 10, stdin) != NULL) {
            if (user_choice[0] == 'n' || user_choice[0] == 'N') {
                run_loop = 0;
            }
        }
    }

    return 0;
}
