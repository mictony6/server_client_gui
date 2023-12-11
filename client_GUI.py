import tkinter as tk
from tkinter import ttk, scrolledtext, Entry, Button, END
import socket
import threading

import pyglet

pyglet.font.add_file('./Inter-Regular.ttf')

# icon path
icon_path = './Animal_Crossing_Leaf.svg.png'


class ChatClient:
    def __init__(self, host, port, client_name):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.client_name = client_name

    def connect(self):
        # Connect to the server
        self.client_socket.connect((self.host, self.port))
        self.client_socket.send(self.client_name.encode('utf-8'))

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


class LoginFrame(tk.Frame):
    def __init__(self, master, chat_app):
        super().__init__(master)
        self.chat_app = chat_app

        self.address_label = ttk.Label(self, text="Enter address:")
        self.address_entry = Entry(self)
        self.name_label = ttk.Label(self, text="Enter your name:")
        self.name_entry = Entry(self)
        self.login_button = Button(self, text="Login", command=self.login)

        self.address_label.pack(pady=5)
        self.address_entry.pack(pady=5)
        self.name_label.pack(pady=5)
        self.name_entry.pack(pady=5)
        self.login_button.pack(pady=10)

    def login(self):
        address = self.address_entry.get()
        name = self.name_entry.get()

        if address and name:
            self.chat_app.client = ChatClient(address, 12345, name)
            self.chat_app.client.connect()
            self.chat_app.show_chat_room_frame()
            self.chat_app.client.send_message("<entered chat room>")



class ChatRoomFrame(tk.Frame):
    def __init__(self, master, chat_app):
        super().__init__(master)
        self.chat_app = chat_app

        # change background color
        self.config(bg="#F4F0E3")

        # canvas to display chat title
        self.canvas = tk.Canvas(self, width=400, height=30, bg="#ABD2B6", bd=0, highlightthickness=0)
        self.canvas.create_text(200, 15, text="NookLink User", font=("Inter", 12, "bold"), fill="#685552")
        self.canvas.pack()

        self.chat_history = scrolledtext.ScrolledText(self, state='disabled', width=40, height=15, bd=0, bg="white",
                                                      font=("Inter", 10), borderwidth=0, highlightthickness=0)
        self.chat_history.pack(padx=10, pady=10)

        input_entry_frame = tk.Frame(self, bg="#F4F0E3")
        input_entry_frame.pack()

        self.input_entry = Entry(input_entry_frame, bd=0, bg="white", font=("Inter", 10))
        self.input_entry.pack(side=tk.LEFT)
        self.send_button = Button(input_entry_frame, font=("Inter", 12, "bold"), text="Send",
               bd=0, fg="#685552", bg="#ABD2B6", activebackground="white", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        self.chat_history.config(state='normal')
        self.chat_history.insert('end', "You entered the chat room" + '\n')
        self.chat_history.config(state='disabled')
        self.chat_history.see(END)


    def send_message(self):
        message = self.input_entry.get()
        if message:
            self.chat_app.client.send_message(message)
            self.update_chat_history(f"You: {message}")
            self.input_entry.delete(0, 'end')

    def update_chat_history(self, message):
        self.chat_history.config(state='normal')
        self.chat_history.insert('end', message + '\n')
        self.chat_history.config(state='disabled')
        self.chat_history.see(END)


class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NookLink")
        self.geometry("400x500")
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

    def close(self):
        print("Goodbye")
        if self.client is not None:
            self.client.running = False
            self.client.send_message("<left the chat room>")
            self.client.client_socket.close()
        self.destroy()

    def show_chat_room_frame(self):
        self.login_frame.pack_forget()
        self.chat_room_frame.pack(fill="both", expand=True)

        # Start a new thread to receive messages
        receive_thread = threading.Thread(target=self.client.receive_messages, args=(self.chat_room_frame,))
        receive_thread.start()


if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
