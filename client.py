import socket
import keyboard
import time

class Client:
    def __init__(self):
        # Initialize socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Initialize server info
        self.ip = "192.168.193.104"
        self.port = 14576

    def connect(self):
        self.socket.connect((self.ip, self.port))
        self.socket.sendall(b"Hello server")
        
        self.listen()

    def send_key_pressed(self, key):
        self.socket.sendall(bytes(str(key), "utf-8"))

    def listen(self):
        while True:
            data = self.socket.recv(1024)

            if not data:
                continue
            else:
                print(f"Received: {data!r}")
                break
        

