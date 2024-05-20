import socket
import threading
import time

# Global variables
HOST = '127.0.0.1'
PORT = 1535
ADDR = (HOST, PORT)
FORMAT = 'utf-8'

# Dictionary to store clients and their usernames
clients = {}
usernames = []


def handle_client(client_socket, client_address):
    username = None

    # Function to broadcast message to all clients
    def broadcast(message, client_sockets):
        print(message)
        for sock in client_sockets:
            if sock != client_socket:
                sock.send(message)
    
    def find_recipient_sockets(recipients):
        recipient_sockets = []
        for sock, uname in clients.items():
            if uname in recipients:
                recipient_sockets.append(sock)
        return recipient_sockets

    try:
        # Ask for username and send welcome message
        username = client_socket.recv(1024).decode(FORMAT)
        usernames.append(username)
        clients[client_socket] = username
        
        
        
        o = f"Hello {username}\n" + " ^ " + str(usernames)
        client_socket.send(o.encode(FORMAT))
        
        

        # Send welcome message to the newly joined user
        mess = f"{username} join the chat room\nHi {username}, welcome to the chat room\n" + " ^ " + str(usernames)
        broadcast(mess.encode(FORMAT), clients.keys())
        

        while True:
            message = client_socket.recv(1024).decode(FORMAT)
        
            # If message is a request for the list of attendees
            if message.strip() == "Please send the list of attendees.":
                print("1")
                attendees = ",".join(clients.values())
                mess = f"Here is the list of attendees:\n{attendees}\n" + " ^ " + str(usernames)
                client_socket.send(mess.encode(FORMAT))
            
            # If message is to leave the chat room
            elif message == "Bye.":
                print("2")
                notification = f"for YoU ^ " + str(usernames)
                client_socket.send(notification.encode(FORMAT))
                mess = f"{username} left the chat room\n" + " ^ " + str(usernames)
                broadcast(mess.encode(FORMAT), clients.keys())
                del clients[client_socket]
                usernames.remove(username)
                break
        
            elif message.startswith("Public message, length="):
                print("3")
                notification = f"for YoU ^ " + str(usernames)
                client_socket.send(notification.encode(FORMAT))
                message = message.split(":")
                mess = f"Public message from {username}, length={len(message)}:{message[1]}" + " ^ " + str(usernames)
                broadcast(mess.encode(FORMAT), clients.keys())
               
            elif message.startswith("Private message, length="):
                print("4")
                notification = f"for YoU ^ " + str(usernames)
                client_socket.send(notification.encode(FORMAT))
                # Extract recipients and message body
                # message_parts = message.split(" to ")
                # message_body = ":".join(message_parts[1:])
                # recipients = 
                message_body = message.split(":") 
                message_body = message_body[1]
                
                recv = message.split(" to ")
                recv = recv[1].split(":")
                recipients = recv[0].split(",")                

                recipient_sockets = find_recipient_sockets(recipients)
                
                print(clients)
                
                print(recipient_sockets)

            
                # Send the private message to the specified recipients
                if recipient_sockets:
                    mess = f"Private message, length={len(message)} to {', '.join(recipients)}:{message_body}" + " ^ " + str(usernames)
                    broadcast(mess.encode(FORMAT), recipient_sockets)
                    print(recipient_sockets)
                else:
                    client_socket.send(f"{message}".encode(FORMAT))
        
            else:
                pass 
    except:
        # If any exception occurs, remove the client and close the connection
        if username:
            del clients[client_socket]
            usernames.remove(username)
            mess = f"{username} left the chat room\n" + " ^ " + str(usernames)
            broadcast(mess.encode(FORMAT))
        client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()

    print("Server is listening on", ADDR)

    while True:
       
        client_socket, client_address = server.accept()
        print(f"Connection from {client_address} has been established!")
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()
  

if __name__ == "__main__":
    start_server()
