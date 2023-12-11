import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ChatServerGUI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.running = True

        self.root = tk.Tk()
        self.root.title("Chat Server")

        # Label to display server address and port
        label_text = f"Server Address: {self.host}, Port: {self.port}"
        self.server_label = tk.Label(self.root, text=label_text, font=("Helvetica", 10, "bold"))
        self.server_label.pack(padx=10, pady=10)

        # Text area to display chat messages
        self.chat_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=20)
        self.chat_text.pack(padx=10, pady=10)

        # Entry field for sending messages
        self.entry_field = tk.Entry(self.root, width=40)
        self.entry_field.pack(pady=10)

        # Button to send messages
        send_button = tk.Button(self.root, text="Send", command=self.send_message)
        send_button.pack()

        # Button to close the server
        close_server_button = tk.Button(self.root, text="Close Server", command=self.close_server)
        close_server_button.pack()

        # Button to restart the server
        restart_server_button = tk.Button(self.root, text="Restart Server", command=self.restart_server)
        restart_server_button.pack()

    def start(self):
        # Bind the socket to a specific address and port
        self.server_socket.bind((self.host, self.port))
        # Listen for incoming connections
        self.server_socket.listen()
        print(f"Server is listening on {self.host}:{self.port}")

        # Start a thread to accept connections
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.start()

        # Start the Tkinter main loop
        self.root.mainloop()

    def send_message(self):
        message = self.entry_field.get()
        if message:
            self.chat_text.insert(tk.END, f"Server: {message}\n")
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
    host = socket.gethostbyname(socket.getfqdn())
    port = 12345  # Port number

    # Create and initialize the ChatServerGUI object
    server_gui = ChatServerGUI(host, port)

    # Start the server with GUI
    server_gui.start()
