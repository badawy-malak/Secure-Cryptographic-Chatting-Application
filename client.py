# Python program to implement client side of chat room.
import socket
import select
import sys
import threading

# Server IP and Port are hard-coded for simplicity.
IP_address = "127.0.0.1"  # Change this to your server's IP if needed.
Port = 12345  # Same as the server port.

# Create a socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((IP_address, Port))

# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            message = server.recv(2048)
            if message:
                print(message.decode('utf-8'))  # Decode the received bytes to string
            else:
                # Server disconnected
                print("Disconnected from server")
                break
        except:
            print("An error occurred!")
            server.close()
            break

# Start the thread to receive messages
threading.Thread(target=receive_messages, daemon=True).start()

# Main loop to send messages
while True:
    message = sys.stdin.readline()
    server.send(message.encode('utf-8'))  # Encode the message to bytes
    sys.stdout.write("<You> ")
    sys.stdout.write(message)
    sys.stdout.flush()

server.close()
