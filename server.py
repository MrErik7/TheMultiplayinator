import socket

class Server:
    def __init__(self, port):
        # Initialize socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Initialize server info
        self.ip = ""
        self.port = port

    def start(self):
        # Bind socket to IP and port
        self.socket.bind((self.ip, self.port))

        # And run the server
        self.run()

    def run(self):
        # Listen for incoming connections
        self.socket.listen()

        while True:
            print("Waiting for connection...")
            self.conn, self.addr = self.socket.accept()
            with self.conn:
                print(f"Connected by {self.addr}")

                while True:
                    if (self.is_open()):
                        try:
                            data = self.conn.recv(1024)
                            if not data:
                                continue
                            print(f"Received: {data}")
                            self.conn.sendall(b"OK")
                        except ConnectionResetError:
                            print("Client disconnected")
                            break

    def stop(self):
        self.running = False
        self.socket.close()

    def is_open(self):
        try:
            self.conn.getpeername()
            return True
        except OSError:
            return False


#server = Server(3333)
#server.start()
