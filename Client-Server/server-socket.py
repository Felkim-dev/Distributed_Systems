from socket import *
import time

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(1)
print("The server is ready to receive")
while True:
    connectionSocket, addr = serverSocket.accept()
    print("From Client:", addr)
    sentence = connectionSocket.recv(1024).decode()
    print("I received:", sentence)
    capitalizedSentence = sentence.upper()
    time.sleep(3)
    connectionSocket.send(capitalizedSentence.encode())
    connectionSocket.close()
