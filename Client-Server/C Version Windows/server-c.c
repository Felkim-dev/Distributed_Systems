#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <winsock2.h>
#include <windows.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

#define PORT 12000
#define BUFFER_SIZE 1024

// Estructura para pasar datos al hilo
typedef struct {
    SOCKET sock;
} ClientData;

// Función que ejecutará cada hilo (equivalente a handle_client en Python)
DWORD WINAPI handle_client(LPVOID lpParam)
{
    ClientData *client_data = (ClientData *)lpParam;
    SOCKET sock = client_data->sock;
    free(client_data); // Liberamos la memoria

    char buffer[BUFFER_SIZE];
    int read_size;

    // Obtener información del cliente (opcional, para logs)
    struct sockaddr_in addr;
    int addr_size = sizeof(struct sockaddr_in);
    getpeername(sock, (struct sockaddr *)&addr, &addr_size);
    printf("--> Nuevo hilo iniciado para: %s\n", inet_ntoa(addr.sin_addr));

    // Recibir mensaje
    // Python: connectionSocket.recv(1024)
    read_size = recv(sock, buffer, BUFFER_SIZE, 0);

    if (read_size > 0)
    {
        buffer[read_size] = '\0'; // Asegurar terminación de string
        printf("Mensaje recibido de %s: %s\n", inet_ntoa(addr.sin_addr), buffer);

        // Convertir a Mayúsculas
        for (int i = 0; buffer[i]; i++)
        {
            buffer[i] = toupper(buffer[i]);
        }

        // Simular proceso largo (Time sleep)
        // Python: time.sleep(3)
        Sleep(3000); // En Windows es Sleep en milisegundos

        // Enviar respuesta
        send(sock, buffer, strlen(buffer), 0);
        printf("<-- Respuesta enviada a %s\n", inet_ntoa(addr.sin_addr));
    }
    else if (read_size == 0)
    {
        printf("El cliente %s cerró la conexión.\n", inet_ntoa(addr.sin_addr));
    }
    else
    {
        printf("Error recibiendo: %d\n", WSAGetLastError());
    }

    // Cerrar socket y terminar hilo
    closesocket(sock);
    return 0;
}

int main()
{
    WSADATA wsaData;
    SOCKET server_fd;
    struct sockaddr_in server_addr, client_addr;
    int client_len = sizeof(client_addr);

    // Inicializar Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        printf("WSAStartup failed: %d\n", WSAGetLastError());
        return 1;
    }

    // 1. Crear el socket
    server_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (server_fd == INVALID_SOCKET)
    {
        printf("No se pudo crear el socket: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }

    // 2. Configurar reuso de dirección (SO_REUSEADDR)
    // Python: serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, (const char *)&opt, sizeof(opt)) == SOCKET_ERROR)
    {
        printf("Fallo en setsockopt: %d\n", WSAGetLastError());
        WSACleanup();
        return 1;
    }

    // Preparar la estructura sockaddr_in
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    // 3. Bind
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == SOCKET_ERROR)
    {
        printf("Fallo en el bind. Puerto ocupado?: %d\n", WSAGetLastError());
        closesocket(server_fd);
        WSACleanup();
        return 1;
    }

    // 4. Listen
    if (listen(server_fd, 5) == SOCKET_ERROR)
    {
        printf("Fallo en listen: %d\n", WSAGetLastError());
        closesocket(server_fd);
        WSACleanup();
        return 1;
    }

    printf("The server is ready to receive (C Language - Multithreaded)\n");

    // 5. Loop principal de aceptación
    while (1)
    {
        SOCKET client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_len);
        if (client_fd == INVALID_SOCKET)
        {
            printf("Error en accept: %d\n", WSAGetLastError());
            continue;
        }

        // Crear un hilo para el cliente
        ClientData *client_data = (ClientData *)malloc(sizeof(ClientData));
        client_data->sock = client_fd;

        HANDLE hThread = CreateThread(NULL, 0, handle_client, (LPVOID)client_data, 0, NULL);
        if (hThread == NULL)
        {
            printf("No se pudo crear el hilo\n");
            free(client_data);
            closesocket(client_fd);
        }
        else
        {
            // Cerrar el handle del hilo (no el hilo en sí)
            CloseHandle(hThread);
        }
    }

    closesocket(server_fd);
    WSACleanup();
    return 0;
}