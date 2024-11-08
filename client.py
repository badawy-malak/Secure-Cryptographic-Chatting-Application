import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext

# Server connection details
IP_address = "127.0.0.1"
Port = 12345

# Connect to the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((IP_address, Port))

# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            message = server.recv(2048)
            if message:
                chat_text_area.config(state=tk.NORMAL)
                chat_text_area.insert(tk.END, message.decode('utf-8') + '\n')
                chat_text_area.yview(tk.END)
                chat_text_area.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Error", "Disconnected from server")
                break
        except Exception as e:
            messagebox.showerror("Error", "An error occurred while receiving messages.")
            server.close()
            break

# Function to send messages to the server
def send_message(event=None):
    message = message_entry.get().strip()
    if message:
        server.send(message.encode('utf-8'))
        message_entry.delete(0, tk.END)

# Function to handle login or registration
def authenticate(action):
    username = simpledialog.askstring("Input", "Enter your username:")
    password = simpledialog.askstring("Input", "Enter your password:", show='*')
    
    if username and password:
        server.send(f"{action} {username} {password}".encode('utf-8'))
        response = server.recv(2048).decode('utf-8')
        messagebox.showinfo("Server Response", response)
        if "Login successful!" in response:
            open_chat_window()
        else:
            messagebox.showwarning("Authentication Failed", "Please try again.")

# Function to open the chat window after successful login
def open_chat_window():
    global chat_window, chat_text_area, message_entry
    
    auth_window.destroy()
    chat_window = tk.Tk()
    chat_window.title("Chat Room")
    
    chat_text_area = scrolledtext.ScrolledText(chat_window, state='disabled', wrap=tk.WORD)
    chat_text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    message_entry = tk.Entry(chat_window)
    message_entry.pack(padx=10, pady=5, fill=tk.X)
    message_entry.bind("<Return>", send_message)
    
    send_button = tk.Button(chat_window, text="Send", command=send_message)
    send_button.pack(pady=5)
    
    threading.Thread(target=receive_messages, daemon=True).start()
    
    chat_window.mainloop()

# Initial window for login/registration
auth_window = tk.Tk()
auth_window.title("Welcome to Chat App")

welcome_label = tk.Label(auth_window, text="Welcome! Please choose an option:", font=("Helvetica", 14))
welcome_label.pack(pady=10)

login_button = tk.Button(auth_window, text="Login", command=lambda: authenticate("LOGIN"))
login_button.pack(pady=5)

register_button = tk.Button(auth_window, text="Register", command=lambda: authenticate("REGISTER"))
register_button.pack(pady=5)

auth_window.mainloop()
