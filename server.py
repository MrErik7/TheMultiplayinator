# echo-server.py
import socket

class Server:
    def __init__(self):
        # Initialize socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Initialize server info
        self.ip = ""
        self.port = 38699

    def start(self):
        # Bind socket to IP and port
        self.socket.bind((self.ip, self.port))

        # Listen for incoming connections
        self.socket.listen()

        while True:
            print("Waiting for connection...")
            conn, addr = self.socket.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    try:
                        data = conn.recv(1024)
                    except ConnectionResetError:
                        print("Client disconnected")
                        break
                    
                    if not data:
                        continue

                    print(f"Received: {data}")
                    conn.sendall(b"Message received")


                    if (data == "quit"):
                        break


server = Server()
server.start()
