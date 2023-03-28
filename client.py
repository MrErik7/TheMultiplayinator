import socket

class Client:
    def __init__(self):
        # Initialize socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip, port):
        self.socket.connect((ip, int(port)))
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
                return data
        
