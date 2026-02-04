#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <arpa/inet.h>
#include <pthread.h>

#define PORT 12000
#define BUFFER_SIZE 1024

/**
 * Thread routine to handle individual client logic.
 * Equivalent to handle_client in the Python implementation.
 */
void *handle_client(void *socket_desc) {
    int sock = *(int*)socket_desc;
    free(socket_desc); // Free the memory allocated in the main loop

    char buffer[BUFFER_SIZE];
    ssize_t read_size;

    // Get client connection details for logging
    struct sockaddr_in addr;
    socklen_t addr_size = sizeof(struct sockaddr_in);
    getpeername(sock, (struct sockaddr*)&addr, &addr_size);
    printf("--> New thread started for: %s\n", inet_ntoa(addr.sin_addr));

    // Receive data from client
    read_size = recv(sock, buffer, BUFFER_SIZE - 1, 0);

    if (read_size > 0) {
        buffer[read_size] = '\0'; // Ensure string termination
        printf("Message received from %s: %s\n", inet_ntoa(addr.sin_addr), buffer);

        // Process data: Convert to uppercase
        for (int i = 0; buffer[i]; i++) {
            buffer[i] = toupper((unsigned char)buffer[i]);
        }

        // Simulate a blocking operation (I/O or processing delay)
        sleep(3);

        // Send the processed response back
        write(sock, buffer, strlen(buffer));
        printf("<-- Response sent to %s\n", inet_ntoa(addr.sin_addr));
    } else if (read_size == 0) {
        printf("Client %s disconnected.\n", inet_ntoa(addr.sin_addr));
    } else {
        perror("Receive error");
    }

    // Cleanup and terminate thread
    close(sock);
    return NULL;
}

int main() {
    int server_fd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);

    // 1. Create socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("Socket creation failed");
        return 1;
    }

    // 2. Set socket options (Reuse Address)
    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        perror("setsockopt failed");
        exit(EXIT_FAILURE);
    }

    // Prepare address structure
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    // 3. Bind socket to port
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed. Port may be in use");
        return 1;
    }

    // 4. Listen for incoming connections
    listen(server_fd, 5);
    printf("Server is ready (C - Multithreaded Mode) on port %d\n", PORT);

    // 5. Main acceptance loop
    while (1) {
        int client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_len);
        if (client_fd < 0) {
            perror("Accept failed");
            continue;
        }

        // Pass the socket descriptor to the thread safely
        int *new_sock = malloc(sizeof(int));
        *new_sock = client_fd;

        pthread_t thread_id;
        if (pthread_create(&thread_id, NULL, handle_client, (void*)new_sock) < 0) {
            perror("Thread creation failed");
            free(new_sock);
            continue;
        }

        // Detach thread to allow automatic resource cleanup upon completion
        pthread_detach(thread_id);
    }

    close(server_fd);
    return 0;
}
