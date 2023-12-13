import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import pyglet

pyglet.font.add_file('./Inter-Regular.ttf')
icon_path = './Animal_Crossing_Leaf.svg.png'

class ChatServerGUI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.running = True

        self.root = tk.Tk()
        self.root.title("Nook Server")
        
        # Customization
        self.root.iconphoto(True, tk.PhotoImage(file=icon_path))   

        # Label to display server address and port
        label_text = f"Server Address: {self.host}\nPort: {self.port}"
        self.server_label = tk.Label(self.root, text=label_text, font=("Inter", 11), foreground="#685552")
        self.server_label.pack(padx=10, pady=17)

        # Text area to display chat messages
        self.chat_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=10, font=("Inter", 9))
        self.chat_text.pack(padx=10, pady=10)
        
        # Entry field for sending messages
        self.entry_field = tk.Entry(self.root, width=30, font=("Inter", 9), foreground="black", background="white")
        self.entry_field.pack(pady=10, side=tk.LEFT, padx=10, ipady=15)

        # Button container for Send, Restart, and Close buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, pady=10, padx=10)

        # Send button
        send_button = tk.Button(button_frame, width=19, text="SEND", command=self.send_message, font=("Inter", 9, "bold"), foreground="white", background="#017c74", bd=2, relief="flat", overrelief="groove")
        send_button.pack(side=tk.TOP)

        # Restart server button
        restart_server_button = tk.Button(button_frame, text="Restart Server", command=self.restart_server, font=("Inter", 8), foreground="#786951", relief="flat", overrelief="groove")
        restart_server_button.pack(side=tk.RIGHT)

        # Close server button
        close_server_button = tk.Button(button_frame, text="Close Server", command=self.close_server, font=("Inter", 8), foreground="white", background="#ef758a", relief="flat", overrelief="groove")
        close_server_button.pack(side=tk.LEFT)

    def start(self):
        # Bind the socket to a specific address and port
        self.server_socket.bind((self.host, self.port))
        # Listen for incoming connections
        self.server_socket.listen()
        print(f"Server is listening on {self.host}:{self.port}")
        # self.chat_text.insert(tk.END, f"Server is listening on {self.host}:{self.port}\n", "message")
    
        # Start a thread to accept connections
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.start()

        # Start the Tkinter main loop
        self.root.mainloop()

    def send_message(self):
        message = self.entry_field.get()
        if message:
            self.chat_text.insert(tk.END, f"Server: {message}\n", "message")
            self.entry_field.delete(0, tk.END)
            self.broadcast(f"Server: {message}".encode('utf-8'))
            

    def accept_connections(self):
        # Main server loop
        while self.running:
            try:
                # Accept a connection from a client
                client_socket, client_address = self.server_socket.accept()
                client_name = client_socket.recv(1024)
                client_name = client_name.decode('utf-8')

                # Add the new client to the list
                self.clients.append(client_socket)

                # Print the address of the new connection
                print(f"Connection from {client_address} named {client_name}")

                # Create and start a new thread to handle the client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_name))
                client_thread.start()

            except socket.error as e:
                # Check if the error is due to the socket being closed
                if self.running:
                    print(f"Error accepting connection: {e}")

    def handle_client(self, client_socket, client_name):
        while self.running:
            try:
                # Receive message from the client
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(client_name, '>', message)
                full_message = f"{client_name}: {message}"
                self.chat_text.insert(tk.END, f"{full_message}\n")
                # Broadcast the message to all clients
                self.broadcast(full_message.encode('utf-8'), sender_socket=client_socket)
            except:
                print(client_name, 'disconnected')
                # Remove the broken connection
                self.clients.remove(client_socket)
                break

    def broadcast(self, message, sender_socket=None):
        for client in self.clients:
            # Send the message to everyone except the sender
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    # Remove the broken connection
                    self.clients.remove(client)

    def close_server(self):
        self.running = False
        self.server_socket.close()
        self.root.destroy()

    def restart_server(self):
        self.running = False
        self.server_socket.close()
        # Create a new server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Start the server again
        self.start()
    
    
if __name__ == "__main__":
    # Server configuration
    host = socket.gethostbyname(socket.gethostname())
    port = 12345  # Port number

    # Create and initialize the ChatServerGUI object
    server_gui = ChatServerGUI(host, port)

    # Start the server with GUI
    server_gui.start()
