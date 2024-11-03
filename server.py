# Python program to implement server side of chat room.
import socket
import sys
from threading import Thread

# Server IP and Port
IP_address = "127.0.0.1"  # Localhost or replace with your server's IP
Port = 12345              # Choose an appropriate port number

# Create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the server to the provided IP address and port
server.bind((IP_address, Port))

# Listen for up to 100 active connections
server.listen(100)
print(f"Server started on {IP_address}:{Port}")

list_of_clients = []

def clientthread(conn, addr):
    # Send a welcome message to the connected client
    conn.send(b"Welcome to this chatroom!")

    while True:
        try:
            # Receive message from client
            message = conn.recv(2048)
            if message:
                # Print the message and address of the client on the server console
                print("<" + addr[0] + "> " + message.decode('utf-8'))

                # Broadcast the message to all other clients
                message_to_send = "<" + addr[0] + "> " + message.decode('utf-8')
                broadcast(message_to_send, conn)
            else:
                # Remove the connection if there is no message (broken connection)
                remove(conn)
                break
        except:
            continue

def broadcast(message, connection):
    for client in list_of_clients:
        if client != connection:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                remove(client)

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

while True:
    # Accept a new connection
    conn, addr = server.accept()

    # Add the new client to the list of clients
    list_of_clients.append(conn)

    # Print the address of the newly connected client
    print(addr[0] + " connected")

    # Create a new thread for each client
    thread = Thread(target=clientthread, args=(conn, addr))
    thread.start()

conn.close()
server.close()
