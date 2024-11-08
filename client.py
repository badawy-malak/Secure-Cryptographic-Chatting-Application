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

# Function to send messages to the server and display them in the chat
def send_message(event=None):
    message = message_entry.get().strip()
    if message:
        server.send(message.encode('utf-8'))
        # Display the sent message in the chat window
        chat_text_area.config(state=tk.NORMAL)
        chat_text_area.insert(tk.END, f"<You>: {message}\n")
        chat_text_area.yview(tk.END)
        chat_text_area.config(state=tk.DISABLED)
        message_entry.delete(0, tk.END)

# Function to handle login or registration
def authenticate(action):
    # Read the initial server welcome message
    initial_response = server.recv(2048).decode('utf-8')
    print(f"Initial server response: {initial_response}")  # Debugging print statement

    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        username = simpledialog.askstring("Input", f"Enter your username for {action}:")
        password = simpledialog.askstring("Input", "Enter your password:", show='*')

        if username and password:
            server.send(f"{action} {username} {password}".encode('utf-8'))
            response = server.recv(2048).decode('utf-8')
            messagebox.showinfo("Server Response", response)

            if "Registration successful!" in response:
                # Registration successful, prompt the user to log in
                messagebox.showinfo("Info", "Registration successful. Please log in.")
                return  # End function to allow user to choose login next
            elif "Login successful!" in response:
                # Login successful, open the chat window
                open_chat_window()
                return  # Exit the function to prevent further prompts
            else:
                attempts += 1
                if attempts < max_attempts:
                    messagebox.showwarning("Authentication Failed", f"Incorrect credentials. You have {max_attempts - attempts} attempt(s) left.")
                else:
                    messagebox.showerror("Authentication Failed", "You have exceeded the maximum number of attempts.")
                    break  # Exit the function after max attempts
        else:
            messagebox.showwarning("Input Required", "Both username and password are required.")

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
