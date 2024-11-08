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

# Initialize the database and create tables if they don't exist
def initialize_db():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            sender TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

initialize_db()

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

# Retrieve all previous messages
def get_previous_messages():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message, timestamp FROM messages ORDER BY timestamp")
    messages = cursor.fetchall()
    conn.close()
    return messages

# Store a new message in the database
def store_message(sender, message):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, message) VALUES (?, ?)", (sender, message))
    conn.commit()
    conn.close()

def clientthread(conn, addr):
    conn.send(b"Welcome to this chatroom! Please register or login.\n")
    authenticated = False
    username = None

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
                        conn.send(b"Username already exists. Enter a different username.\n")
                elif msg.startswith("LOGIN"):
                    _, username, password = msg.split()
                    if login_user(username, password):
                        conn.send(b"Login successful! You can now start chatting.\n")
                        authenticated = True
                        list_of_clients.append((conn, username))  # Add authenticated client and their username

                        # Send previous messages to the user
                        previous_messages = get_previous_messages()
                        for sender, msg, timestamp in previous_messages:
                            conn.send(f"{sender} ({timestamp}): {msg}\n".encode('utf-8'))
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
                print(f"<{username}> {decoded_message}")
                store_message(username, decoded_message)  # Store the message in the database
                broadcast(f"{username}: {decoded_message}", conn)
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
    for client, _ in list_of_clients:
        if client != connection:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message to client: {e}")
                client.close()
                remove(client, None)

def remove(connection, addr=None):
    for client, username in list_of_clients:
        if client == connection:
            list_of_clients.remove((client, username))
            if addr:
                print(f"Client {addr[0]} ({username}) disconnected.")
            else:
                print("A client disconnected.")
            connection.close()
            break

while True:
    conn, addr = server.accept()
    print(f"{addr[0]} connected")
    thread = Thread(target=clientthread, args=(conn, addr))
    thread.start()

conn.close()
server.close()
