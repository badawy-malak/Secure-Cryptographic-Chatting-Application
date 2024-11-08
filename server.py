import socket
import sys
from threading import Thread
import sqlite3

# Server IP and Port
IP_address = "127.0.0.1"
Port = 12345

# Create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((IP_address, Port))
server.listen(100)
print(f"Server started on {IP_address}:{Port}")

list_of_clients = []

# Database connection
def db_connection():
    conn = sqlite3.connect('Secure_Chatting_Application_DB.db')
    return conn

# User registration
def register_user(username, password):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# User login
def login_user(username, password):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def clientthread(conn, addr):
    conn.send(b"Welcome to this chatroom! Please register or login.\n")
    authenticated = False

    while not authenticated:
        try:
            message = conn.recv(2048)
            if message:
                msg = message.decode('utf-8').strip()
                if msg.startswith("REGISTER"):
                    _, username, password = msg.split()
                    if register_user(username, password):
                        conn.send(b"Registration successful! Please login.\n")
                    else:
                        conn.send(b"Username already exists. Try a different one.\n")
                elif msg.startswith("LOGIN"):
                    _, username, password = msg.split()
                    if login_user(username, password):
                        conn.send(b"Login successful! You can now start chatting.\n")
                        authenticated = True
                        list_of_clients.append(conn)  # Add authenticated client to the list
                    else:
                        conn.send(b"Invalid username or password. Please try again.\n")
            else:
                remove(conn, addr)
                break
        except ConnectionResetError:
            print(f"Client {addr[0]} disconnected abruptly.")
            remove(conn, addr)
            break
        except Exception as e:
            print(f"Error during authentication: {e}")
            remove(conn, addr)
            break

    # Start chat mode only if authenticated
    while authenticated:
        try:
            message = conn.recv(2048)
            if message:
                decoded_message = message.decode('utf-8')
                print(f"<{addr[0]}> {decoded_message}")
                broadcast(f"<{addr[0]}> {decoded_message}", conn)
            else:
                remove(conn, addr)
                break
        except ConnectionResetError:
            print(f"Client {addr[0]} disconnected abruptly.")
            remove(conn, addr)
            break
        except Exception as e:
            print(f"Error during message handling: {e}")
            remove(conn, addr)
            break

def broadcast(message, connection):
    for client in list_of_clients:
        if client != connection:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message to client: {e}")
                client.close()
                remove(client, None)

def remove(connection, addr=None):
    if connection in list_of_clients:
        list_of_clients.remove(connection)
        if addr:
            print(f"Client {addr[0]} disconnected.")
        else:
            print("A client disconnected.")
        connection.close()

while True:
    conn, addr = server.accept()
    print(f"{addr[0]} connected")
    thread = Thread(target=clientthread, args=(conn, addr))
    thread.start()

conn.close()
server.close()
