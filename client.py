import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, Listbox, Toplevel, Button, MULTIPLE
from datetime import datetime
import ast


# Global variables
HOST = '127.0.0.1'
PORT = 1535
FORMAT = 'utf-8'
MAIN_USERS = []
USERNAME = str


def receive_messages(client_socket, text_area, attendees_listbox, username):
    while True:
        global i

        message = client_socket.recv(1024).decode(FORMAT)
        message = message.split("^")
        usernames = ast.literal_eval(message[1])
        message = message[0]

        c = datetime.now()
        current_time = c.strftime('%H:%M')
        if message.startswith("Enter "):
            print("ENTER")
        elif message.startswith("Public message "):
            print("PUBLIC")
            parts = message.split(":")
            sender_info = parts[0].split(",")
            sender = sender_info[0].split("from ")[1].strip()
            message_body = parts[1].strip()
            print(len(usernames))
            attendees_listbox.delete(0, tk.END)
            for user in usernames:
                print(usernames)
                attendees_listbox.insert(tk.END, user)
            text_area.insert(tk.END, f"{sender} : {message_body} \n{current_time}\n\n")

        elif message.startswith("Private message, "):
            print("PRIVATE")
            mess = message.split(":")
            message = str(mess[1]).strip()
            attendees_listbox.delete(0, tk.END)
            for user in usernames:
                attendees_listbox.insert(tk.END, user.strip())
            text_area.insert(tk.END, f"Private message for you : {message} \n{current_time}\n\n")

        elif message.startswith("Here is "):
            print("HERE")
            attendees = message.split(":")[1].strip().split(",")
            print(attendees)
            attendees_listbox.delete(0, tk.END)  # Clear the listbox
            for attendee in attendees:
                attendees_listbox.insert(tk.END, attendee.strip())
            print(attendees)
            text_area.insert(tk.END, f"People in the chat: {', '.join(attendees)} \n{current_time}\n\n")

        elif message.startswith("Hello "):
            print("HELLO")
            attendees_listbox.delete(0, tk.END)  # Clear the listbox
            text_area.insert(tk.END, message + "\n\n")
            for user in usernames:
                attendees_listbox.insert(tk.END, user)

        else:
            attendees_listbox.delete(0, tk.END)
            for user in usernames:
                attendees_listbox.insert(tk.END, user)
                
        MAIN_USERS = usernames
        

def send_public_message(client_socket, username, message, text_area):
    c = datetime.now()
    current_time = c.strftime('%H:%M')
    if len(message) != 0:
        text_area.insert(tk.END, "You : " + message + "\n" + current_time + "\n\n")
        message = f"Public message, length={len(message)}: {message}"
        client_socket.send(message.encode(FORMAT))
    else: pass

def send_private_message(client_socket, username, recipients, message):
    if recipients and message:
        recipient_string = ",".join(recipients)
        message = f"Private message, length={len(message)} to {recipient_string}: {message}"
        client_socket.send(message.encode(FORMAT))

def request_attendees(client_socket):
    client_socket.send("Please send the list of attendees.".encode(FORMAT))

def send_bye_message(client_socket):
    client_socket.send("Bye.".encode(FORMAT))

def send_bye(client_socket):
        send_bye_message(client_socket)
        client_socket.close()
        exit()

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Create GUI window
    root = tk.Tk()
    root.title("Chat Client")

    # Prompt user for username
    username = simpledialog.askstring("Username", "Enter your username:")
    USERNAME = username
    if username:
        client_socket.send(username.encode(FORMAT))

    # Create text area
    text_area = scrolledtext.ScrolledText(root, font=("Times New Roman", 15))
    text_area.config(bg="white", fg="black", height=50, width=40)
    text_area.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)
    text_area.insert(tk.END, f"Hi {username}, welcome to the chat room\n")

    # Create attendees listbox
    attendees_listbox = Listbox(root, font=("Times New Roman", 15))
    attendees_listbox.config(height=5, width=5)
    attendees_listbox.pack(padx=10, pady=10, side=tk.TOP, fill=tk.BOTH, expand=True)
    attendees_listbox.insert(tk.END, "Attendees")

    # Function to send public message
    def send_public():
        message = entry.get()
        send_public_message(client_socket, username, message, text_area)
        entry.delete(0, tk.END)

    # Function to send private message
    def send_private():
        def on_select():
            selected_indices = recipients_listbox.curselection()
            selected_users = [recipients_listbox.get(i) for i in selected_indices]
            message = message_entry.get()
            if selected_users and message:
                send_private_message(client_socket, username, selected_users, message)
            private_window.destroy()

        # Create new window for selecting recipients
        private_window = Toplevel(root)
        private_window.title("Private Message")

        tk.Label(private_window, text="Select recipients:").pack(padx=10, pady=5)
        recipients_listbox = Listbox(private_window, selectmode=MULTIPLE)
        recipients_listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Populate listbox with attendees
        for i in range(attendees_listbox.size()) :
            if attendees_listbox.get(i) == USERNAME: 
                continue
            else :
                recipients_listbox.insert(tk.END, attendees_listbox.get(i))

        tk.Label(private_window, text="Enter your message:").pack(padx=10, pady=5)
        message_entry = tk.Entry(private_window)
        message_entry.pack(padx=10, pady=5, fill=tk.X)

        tk.Button(private_window, text="Send", command=on_select).pack(padx=10, pady=5)

    # Function to request attendees
    def request_attendees_func():
        request_attendees(client_socket)

    # Function to send "Bye." message
    def send_bye():
        send_bye_message(client_socket)
        client_socket.close()
        exit()

    # Function to clear text area
    def clear_text_area():
        text_area.delete('1.0', tk.END)

    # Entry for typing message
    entry = tk.Entry(root, width=50)
    entry.pack(padx=10, pady=10)

    # Button to send public message
    send_public_button = tk.Button(root, text="Send Public", command=send_public)
    send_public_button.pack(padx=10, pady=5)

    # Button to send private message
    send_private_button = tk.Button(root, text="Send Private", command=send_private)
    send_private_button.pack(padx=10, pady=5)

    # Button to request attendees
    request_attendees_button = tk.Button(root, text="Show Attendees", command=request_attendees_func)
    request_attendees_button.pack(padx=10, pady=5)

    # Button to send "Bye." message
    exit_button = tk.Button(root, text="Exit", command=send_bye)
    exit_button.pack(padx=10, pady=5)

    # Button to clear text area
    clear_text_area_button = tk.Button(root, text="Clear", command=clear_text_area)
    clear_text_area_button.pack(padx=10, pady=5)

    # Start a thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, text_area, attendees_listbox, username))
    receive_thread.start()

    root.mainloop()

if __name__ == "__main__":
    main()
