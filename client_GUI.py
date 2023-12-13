import tkinter as tk
from tkinter import ttk, scrolledtext, Entry, Button, END
import socket
import threading
import pyglet

pyglet.font.add_file('./Inter-Regular.ttf')

# icon path
icon_path = './Animal_Crossing_Leaf.svg.png'

# Connecting to the server and sending/receiving messages
class ChatClient:
    def __init__(self, host, port, client_name): 
        self.host = host                                                        # Get local machine name
        self.port = port                                                        # Reserve a port for your service.
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket object
        self.running = True                                                     # Boolean to keep the client running
        self.client_name = client_name                                          # Client name

    def connect(self):
        self.client_socket.connect((self.host, self.port))                      # Connect to the server                 
        self.client_socket.send(self.client_name.encode('utf-8'))               # After connecting, send client name to the server

    def receive_messages(self, chat_room_frame): 
        while self.running:
            try:
                # Receive message from the server
                message = self.client_socket.recv(1024)
                chat_room_frame.update_chat_history(message.decode('utf-8'))
            except:
                # If an error occurs, close the connection
                print("Connection closed.")
                self.client_socket.close() 
                self.running = False
                break

    def send_message(self, message):
        # Send the message to the server
        self.client_socket.send(message.encode('utf-8'))
    
# Displays the login frame and connecting to the server
class LoginFrame(tk.Frame):
    def __init__(self, master, chat_app):                                       # master is the ChatApp object
        super().__init__(master)                                                # Initialize the parent class
        self.chat_app = chat_app                                                
        
        # Canvas to display chat title
        self.canvas = tk.Canvas(self, width=400, height=50)
        self.canvas.create_text(200, 40, text="NookLink", font=("Inter", 18, "bold"), fill="#68b893")
        self.canvas.pack()
        
        self.address_label = ttk.Label(self, text="Enter address:", font=("Inter", 12))
        self.address_entry = Entry(self, font=("Inter", 12))
        self.name_label = ttk.Label(self, text="Enter your name:", font=("Inter", 12))
        self.name_entry = Entry(self, font=("Inter", 12))
        self.login_button = Button(self, text="LOGIN", command=self.login, font=("Inter", 12, "bold"), fg="#786951",
                                   bg="#fff9e5", activebackground="#f8eebc", relief="flat", overrelief="groove")

        # Place widgets
        self.address_label.pack(pady=15)
        self.address_entry.pack(pady=5)
        self.name_label.pack(pady=5)
        self.name_entry.pack(pady=5)
        self.login_button.pack(pady=10)

    def login(self):                                                           
        address = self.address_entry.get()                                      # Get address from the address entry field                                    
        name = self.name_entry.get()                                            # Get name from the name entry field  

        if address and name:                                                    # If address and name are not empty
            self.chat_app.client = ChatClient(address, 12345, name)
            self.chat_app.client.connect()
            self.chat_app.show_chat_room_frame()
            self.chat_app.client.send_message("<entered chat room>")
        else:
            print("Address and Name required.")

# Displays chat room frame and sending messages
class ChatRoomFrame(tk.Frame):  
    def __init__(self, master, chat_app):                                       # master is the ChatApp object                                     
        super().__init__(master)                                                # Initialize the parent class
        self.chat_app = chat_app                                                # ChatApp object                                        

        # change background color
        self.config(bg="#F4F0E3")

        # text area to display chat messages
        self.chat_history = scrolledtext.ScrolledText(self, state='disabled', height=15, bg="white",
                                                      font=("Inter", 10), borderwidth=0, highlightthickness=0) 
        self.chat_history.pack(padx=10, pady=10)
        
        # input frame
        input_frame = tk.Frame(self, bg="#F4F0E3")
        input_frame.pack(pady=10, padx=10)
        
        self.input_entry = Entry(input_frame, bg="white", font=("Inter", 10))
        self.input_entry.pack(pady=10, side=tk.LEFT, ipady=50, padx=10, ipadx=40, fill="both", expand=True)
        self.send_button = Button(input_frame, font=("Inter", 10, "bold"), text="SEND", width=10, height=30,
               bd=0, fg="white", bg="#017c74", activebackground="white", command=self.send_message)
        self.send_button.pack(side=tk.TOP, pady=10, ipadx=30)

        self.chat_history.config(state='normal')
        self.chat_history.insert('end', "You entered the chat room" + '\n')
        self.chat_history.config(state='disabled')
        self.chat_history.see(END)
        
    # Send message to the server
    def send_message(self):
        message = self.input_entry.get()
        if message:
            self.chat_app.client.send_message(message)
            self.update_chat_history(f"You: {message}")
            self.input_entry.delete(0, 'end')

    # Update chat history
    def update_chat_history(self, message):
        self.chat_history.config(state='normal')                                # Set state to normal to allow editing          
        self.chat_history.insert('end', message + '\n')                         # Insert message to the end of the text area
        self.chat_history.config(state='disabled')
        self.chat_history.see(END)

# Displays the login frame and chat room frame
class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()                                                     # Initialize the parent class
        self.title("NookLink")
        self.geometry("400x350") 
        self.client = None

        # Setting icon of master window
        icon = tk.PhotoImage(file=icon_path)
        self.iconphoto(False, icon)
        
        self.login_frame = LoginFrame(self, self) 
        self.chat_room_frame = ChatRoomFrame(self, self)

        self.login_frame.pack(fill="both", expand=True)
        self.chat_room_frame.pack(fill="both", expand=True)
        self.chat_room_frame.pack_forget()

        self.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):                                                            # Close the client and destroy the window
        print("Goodbye")
        if self.client is not None:
            self.client.running = False
            self.client.send_message("<left the chat room>")
            self.client.client_socket.close()
        self.destroy()

    def show_chat_room_frame(self):                                             # Show the chat room frame and start receiving messages
        self.login_frame.pack_forget()
        self.chat_room_frame.pack(fill="both", expand=True)

        # Start a new thread to receive messages
        receive_thread = threading.Thread(target=self.client.receive_messages, args=(self.chat_room_frame,))
        receive_thread.start()

# Creates a ChatApp object and starts the main loop
if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
