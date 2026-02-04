#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

#define SERVER_ADDRESS "172.23.210.60"
#define SERVER_PORT 12000
#define BUFFER_SIZE 1024

int main() {
    WSADATA wsaData;
    SOCKET clientSocket;
    struct sockaddr_in serverAddr;
    char serverName[] = SERVER_ADDRESS;
    int serverPort = SERVER_PORT;
    int next = 1;
    char sentence[BUFFER_SIZE];
    char modifiedSentence[BUFFER_SIZE];
    char otherMessage;
    int recvBytes;

    // Initialize Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        printf("WSAStartup failed: %d\n", WSAGetLastError());
        return 1;
    }

    while (next) {
        // Create socket
        clientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (clientSocket == INVALID_SOCKET) {
            printf("Socket creation failed: %d\n", WSAGetLastError());
            WSACleanup();
            return 1;
        }

        // Setup server address structure
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(serverPort);
        serverAddr.sin_addr.s_addr = inet_addr(serverName);

        // Connect to server
        if (connect(clientSocket, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
            printf("Connection failed: %d\n", WSAGetLastError());
            closesocket(clientSocket);
            break;
        }

        // Get sentence input
        printf("Input lowercase sentence: ");
        fgets(sentence, sizeof(sentence), stdin);
        
        // Remove newline if present
        size_t len = strlen(sentence);
        if (len > 0 && sentence[len - 1] == '\n') {
            sentence[len - 1] = '\0';
        }

        // Send sentence to server
        if (send(clientSocket, sentence, strlen(sentence), 0) == SOCKET_ERROR) {
            printf("Send failed: %d\n", WSAGetLastError());
            closesocket(clientSocket);
            break;
        }

        // Receive modified sentence from server
        recvBytes = recv(clientSocket, modifiedSentence, sizeof(modifiedSentence) - 1, 0);
        if (recvBytes <= 0) {
            printf("Connection lost\n");
            next = 0;
            closesocket(clientSocket);
            break;
        } else {
            modifiedSentence[recvBytes] = '\0';
            printf("From Server: %s\n", modifiedSentence);
        }

        // Ask if user wants to send another message
        printf("Other message: (Y/N) ");
        scanf(" %c", &otherMessage);
        getchar(); // consume the newline

        if (otherMessage == 'N' || otherMessage == 'n') {
            next = 0;
        }

        // Close socket
        closesocket(clientSocket);
    }

    // Cleanup Winsock
    WSACleanup();
    return 0;
}
