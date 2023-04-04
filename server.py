# echo-server.py
import socket
import json
import time

class Server:
    def __init__(self):
        # Initialize socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Initialize server info
        self.ip = ""
        self.port = 14576


    def start(self):
        # Bind socket to IP and port
        self.socket.bind((self.ip, self.port))


    def await_connections(self):
        # Listen for incoming connections
        self.socket.listen()

        while True:
            print("Waiting for connection...")
            self.conn, self.addr = self.socket.accept()
            with self.conn:
                print(f"Connected by {self.addr}")
                break
    
    def listen(self):
        try:
            data = self.conn.recv(1024)
            print(f"Received: {data}")
            self.conn.sendall(b"OK")
            return data
            
        except ConnectionResetError:
            print("Client disconnected")
            return "disconnected"
