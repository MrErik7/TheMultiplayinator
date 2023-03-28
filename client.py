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
        

client = Client()
client.connect()
while True:
    try:

        # https://www.circuitbasics.com/how-to-detect-keyboard-and-mouse-inputs-on-a-raspberry-pi/
        if (keyboard.read_key() in "w"):
            client.send_key_pressed("w")

        elif (keyboard.read_key() in "a"):
            client.send_key_pressed("a")

        elif (keyboard.read_key() in "s"):
            client.send_key_pressed("s")
            
        elif (keyboard.read_key() in "d"):
            client.send_key_pressed("d")

        client.listen()
        
    except ConnectionResetError:
        print("Lost connection to server. Reconnecting...")
        client.connect()