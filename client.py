import socket
import threading
import tkinter as tk
from tkinter import simpledialog, Listbox, Toplevel, MULTIPLE
from datetime import datetime
import ast
import customtkinter
import time 

# Global variables
HOST = '127.0.0.1'
PORT = 1533
FORMAT = 'utf-8'
MAIN_USERS = []
MESSAGES = []
USERNAME = str
I = 0
CUREENT_TIME = str
SENDER = str
ALONE = True

# Configs
customtkinter.set_appearance_mode("dark")  

                
def save_history():
    global MESSAGES
    
    try : 
        with open(f"{USERNAME}.txt", "r+") as file: 
            for i in MESSAGES: 
                file.write(i)
    except : 
        with open(f"{USERNAME}.txt", "w+") as file: 
            file.write(f"username : {USERNAME} \n")
            for i in MESSAGES: 
                file.write(i)
              
def create_message_bubble(frame, message, alignment):
    global CUREENT_TIME
    global GREY_FLAG
    
    timestamp = time.strftime('%H:%M')
    
    if CUREENT_TIME != timestamp:
        textlabel = customtkinter.CTkLabel(master=frame, text=timestamp, font=("Roboto", 16), corner_radius=32, text_color="grey")
        textlabel.pack(padx=3)
    CUREENT_TIME = timestamp
    
    if alignment == "p": 
        textlabel = customtkinter.CTkLabel(master=frame, text=message, fg_color="red", font=("Roboto", 16), corner_radius=32, text_color="white")
        textlabel.pack(ipady=3, pady=5, padx=3, anchor="w")
        
    elif alignment == "u": 
        textlabel = customtkinter.CTkLabel(master=frame, text=message, fg_color="green", text_color="white", corner_radius=16, font=("Roboto", 16))
        textlabel.pack(ipady=3, pady=5, padx=20, anchor="e")
    
    elif alignment == "n": 
        textlabel = customtkinter.CTkLabel(master=frame, text=message, font=("Roboto", 12), corner_radius=32, text_color="grey")
        textlabel.pack(padx=3)
        
    elif alignment == "s": 
        textlabel = customtkinter.CTkLabel(master=frame, text=message, font=("Roboto", 12), corner_radius=32, text_color="grey")
        textlabel.pack(ipady=1, pady=1, anchor="w")
        
    else: 
        textlabel = customtkinter.CTkLabel(master=frame, text=message, fg_color="black", font=("Roboto", 16), corner_radius=32, text_color="white")
        textlabel.pack(ipady=3, pady=5, padx=3, anchor="w")
    frame._parent_canvas.yview_moveto(5.0)
    

def receive_messages(client_socket, message_frame, attendees_listbox):    
    
    while True:
        global MAIN_USERS
        global MESSAGES
        global SENDER
        global USERNAME
        global ALONE
        
        message = client_socket.recv(1024).decode(FORMAT)
        message = message.split("^")
        usernames = list(set(ast.literal_eval(message[1])))
        message = message[0]
        
        if message.startswith("Enter "):
            pass
        elif message.startswith("Public message "):
            parts = message.split(":")
            sender_info = parts[0].split(",")
            sender = sender_info[0].split("from ")[1].strip()
            message_body = parts[1].strip()
            attendees_listbox.delete(0, tk.END)
            MESSAGES.append(f"p , {message_body} \n")
            for user in usernames:
                if user == USERNAME: 
                    pass
                else:
                    attendees_listbox.insert(tk.END, "  " + user)
            if sender != SENDER: 
                create_message_bubble(message_frame, f"{sender} :", "s")
                SENDER = sender
            create_message_bubble(message_frame, f"{message_body}", 'w')
            

        elif message.startswith("Private message, "):
            print(message)
            print(usernames)
            mess = message.split(":")
            message = str(mess[1]).strip()
            people = mess[0].split("to")
            senders = people[1].split("from")
            sender = senders[1].strip()
            print(senders)
            print(sender)
            attendees_listbox.delete(0, tk.END)
            for user in usernames:
                if user == USERNAME: 
                    pass
                else:
                    attendees_listbox.insert(tk.END, "  " + user.strip()) 
            if sender != SENDER: 
                create_message_bubble(message_frame, f"{sender} :", "s")
                SENDER = sender
            create_message_bubble(message_frame, message=message, alignment="p")
            MESSAGES.append(f"pr , {message} \n")

        elif message.startswith("Here is "):
            attendees = message.split(":")[1].strip().split(",")
            attendees_listbox.delete(0, tk.END)  # Clear the listbox
            for attendee in attendees:
                if attendee == USERNAME: 
                    pass
                else:
                    attendees_listbox.insert(tk.END, "  " + attendee)
            create_message_bubble(message_frame, f"People in the chat: {', '.join(attendees)}", 'n')
            SENDER = None

        elif message.startswith("Hello "):
            attendees_listbox.delete(0, tk.END)  # Clear the listbox
            create_message_bubble(message_frame, message, 'n')
            for user in usernames:
                if user == USERNAME: 
                    pass
                else:
                    attendees_listbox.insert(tk.END, "  " + user)
            SENDER = None
        
        elif "left the chat" in message: 
            if len(usernames) == 1: 
                ALONE = True
            message = message.strip()
            create_message_bubble(message_frame, f"{message}", 'n')
            attendees_listbox.delete(0, tk.END)
            for user in usernames:
                if user == USERNAME: 
                    pass
                else:
                    attendees_listbox.insert(tk.END, "  " + user)
            SENDER = None
                
        elif "joined the chat" in message: 
            create_message_bubble(message_frame, message, "n")
            attendees_listbox.delete(0, tk.END)
            for user in usernames:
                if user == USERNAME: 
                    pass
                else:
                    attendees_listbox.insert(tk.END, "  " + user)
            SENDER = None
            
        else:
            attendees_listbox.delete(0, tk.END)
            for user in usernames:
                if user == USERNAME: 
                    pass
                else:
                    attendees_listbox.insert(tk.END, "  " + user)
            SENDER = None
        if len(usernames) == 1 and ALONE == True: 
            create_message_bubble(message_frame, "You're alone in this chat", "n")
            ALONE = False
                
        MAIN_USERS = usernames

def send_public_message(client_socket, username, message, message_frame):
    global MESSAGES
    global SENDER 
    SENDER = None
    c = datetime.now()
    if len(message) != 0:
        create_message_bubble(message_frame, message, alignment="u")
        MESSAGES.append(f"u , {message} \n")
        message = f"Public message, length={len(message)}: {message}"
        client_socket.send(message.encode(FORMAT))
    else: pass

def send_private_message(client_socket, username, recipients, message):
    if recipients and message:
        recipient_string = ",".join(recipients).strip()
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
    global MESSAGES
    global USERNAME
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    
    # Create GUI window
    root = tk.Tk()
    root.title("Chat Client")
    root.config(bg="black") 

    # Prompt user for username
    while True: 
        username = simpledialog.askstring("Username", "Enter your username:")
    
        USERNAME = username
        if username:
            client_socket.send(username.encode(FORMAT))
            break
        
    message_frame = tk.Frame(root,bg="black")
    message_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scrollable_frame = customtkinter.CTkScrollableFrame(
    master=message_frame, height=650, width=450, corner_radius=5)
    scrollable_frame.pack(pady=8, padx=10, fill="both", expand=True, side="top")
    
    create_message_bubble(scrollable_frame, f"Hi {username}, welcome to the chat room", 'n')

    # Create attendees listbox
    attendees_listbox = Listbox(root, font=("Roboto", 16))
    attendees_listbox.config(height=5, width=5)
    attendees_listbox.config(bg="grey")   
    attendees_listbox.pack(padx=10, pady=10, side=tk.TOP, fill=tk.BOTH, expand=True)
    attendees_listbox.insert(tk.END, "Attendees")

    # Function to send public message
    def send_public():
        message = entry.get()
        send_public_message(client_socket, username, message, scrollable_frame)
        entry.delete(0, tk.END)

    # Function to send private message
    def send_private():
        global MAIN_USERS
        
        def on_select():
            selected_indices = recipients_listbox.curselection()
            selected_users = [recipients_listbox.get(i) for i in selected_indices]
            message = message_entry.get()
            if selected_users and message:
                send_private_message(client_socket, username, selected_users, message)
            private_window.destroy()
        
        if len(MAIN_USERS) == 1 or len(MAIN_USERS) == 0: 
            send_private_button.configure(text="You're alone :(")
            take_a_walk_threading = threading.Thread(target=take_a_walk, args=())
            take_a_walk_threading.start()
            
        else:
            # Create new window for selecting recipients
            private_window = Toplevel(root)
            private_window.title("Private Message")

            customtkinter.CTkLabel(private_window, text="Select recipients",fg_color="royalblue",text_color="white", corner_radius=32).pack(padx=10, pady=8)
            recipients_listbox = Listbox(private_window, selectmode=MULTIPLE)
            recipients_listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

            # Populate listbox with attendees
            for i in range(attendees_listbox.size()) :
                if attendees_listbox.get(i) == USERNAME: 
                    continue
                else :
                    recipients_listbox.insert(tk.END, attendees_listbox.get(i))

            customtkinter.CTkLabel(private_window, text="Enter your message",text_color="white",fg_color="royalblue", corner_radius=32).pack(padx=10, pady=8)
            message_entry = customtkinter.CTkEntry(private_window, placeholder_text="Message...")
            message_entry.pack(padx=10, pady=5, fill=tk.X)
            tk.Button(private_window, text="Send", command=on_select).pack(padx=10, pady=5)

    # Function to request attendees
    def request_attendees_func():
        request_attendees(client_socket)

    # Function to send "Bye." message
    def send_bye():
        save_history()
        send_bye_message(client_socket)
        client_socket.close()
        exit()

    # Function to clear text area
    def clear_text_area():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        create_message_bubble(scrollable_frame, "History deleted", alignment="n")
    
    
    def load_history(): 
        create_message_bubble(scrollable_frame, "Old messages", "n")
        global MESSAGES
        try : 
        
            with open(f"{USERNAME}.txt", "r") as file: 
                lines = file.readlines()
                lines.pop(0)
                for i in lines: 
                    parts = i.split(",")
                    parts[0] = parts[0].strip()
                    if parts[0] == "p": 
                        create_message_bubble(scrollable_frame, parts[1].strip(), "w" )
                    elif parts[0] == "pr": 
                        create_message_bubble(scrollable_frame, parts[1].strip(), "p" )
                    elif parts[0] == "u": 
                        create_message_bubble(scrollable_frame, parts[1].strip(), "u" )
            create_message_bubble(scrollable_frame, "New messages", alignment="n")
            scrollable_frame._parent_canvas.yview_moveto(5.0)
        except Exception as e:
            print(e)
            pass
        
        
    def change_theme(): 
        global I 
        if I == 0: 
            customtkinter.set_appearance_mode("light") 
            root.config(bg="white")     
            attendees_listbox.config(bg="lightgrey", fg="grey")   
            message_frame.config(bg="white")
            I = 1 
        else: 
            customtkinter.set_appearance_mode("dark")  
            root.config(bg="black") 
            attendees_listbox.config(bg="grey", fg="white")
            message_frame.config(bg="black") 
            I = 0
    
    
    def take_a_walk(): 
        time.sleep(3)
        send_private_button.configure(text="Send Private")
        
    # Entry for typing message
    entry = customtkinter.CTkEntry(message_frame, width=500, placeholder_text="Message...")
    entry.pack(padx=10, pady=10,side="bottom")

    # Button to send public message
    send_public_button = customtkinter.CTkButton(root, text="Send", command=send_public)
    send_public_button.pack(padx=10, pady=5)

    # Button to send private message
    send_private_button = customtkinter.CTkButton(root, text="Send Private", command=send_private)
    send_private_button.pack(padx=10, pady=5)

    # Button to request attendees
    request_attendees_button = customtkinter.CTkButton(root, text="Show Attendees", command=request_attendees_func)
    request_attendees_button.pack(padx=10, pady=5)

    # Button to clear text area
    clear_text_area_button = customtkinter.CTkButton(root, text="Clear", command=clear_text_area)
    clear_text_area_button.pack(padx=10, pady=5)
    
    load_history_button = customtkinter.CTkButton(root, text="Load History", command=load_history)
    load_history_button.pack(padx=10, pady=5)
    
    change_theme_button = customtkinter.CTkButton(root, text="Theme", command=change_theme)
    change_theme_button.pack(padx=10, pady=5)
    
    # Button to send "Bye." message
    exit_button = customtkinter.CTkButton(root, text="Exit", command=send_bye)
    exit_button.pack(padx=10, pady=5)

    # Start a thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, scrollable_frame, attendees_listbox))
    receive_thread.start()
    
    root.mainloop()

if __name__ == "__main__":
    main()
