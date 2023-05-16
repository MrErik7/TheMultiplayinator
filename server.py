import socket
import threading

class Server:
    def __init__(self, port, max_clients=5):
        # Initialize socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Initialize server info
        self.ip = ""
        self.port = port

        # Initialize client info
        self.max_clients = max_clients
        self.clients = []

        # Initialize server lock
        self.lock = threading.Lock()

        # Initialize callback function
        self.callback = None

    # This method sends back data, such as ip of clients and key pressed, to main script, as a callback function
    def set_callback(self, callback):
        self.callback = callback


    def start(self):
        # Bind socket to IP and port
        self.socket.bind((self.ip, self.port))

        # And run the server
        self.run()

    def run(self):
        # Listen for incoming connections
        self.socket.listen()

        while True:
            # Accept incoming connections
            try:
                conn, addr = self.socket.accept()
            except OSError:
                # Socket has been closed
                break

            # Verify client connection
            if len(self.clients) < self.max_clients:
                self.clients.append(conn)
                if self.callback:
                    self.callback(addr[0], "ip-add")

                thread = threading.Thread(target=self.listen_to_client, args=(conn, addr))
                thread.start()
            else:
                conn.sendall(b"Server is full")
                conn.close()

        # Close all client sockets
        with self.lock:
            for conn in self.clients:
                conn.close()

    # This method will just send and recieve messages from the clients, to verify their status, also recieve the keys
    def listen_to_client(self, conn, addr):
        print(f"Connected by {addr}")
        with self.lock:
            self.clients.append(conn)

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                if data.startswith(b"key:"):
                    key = data.split(b":")[1].decode().strip()
                    print(f"Client {addr} pressed key {key}")
                    conn.sendall(b"KEY RECIEVED")
                    if self.callback:
                        self.callback(key, "key")

                elif data.startswith(b"key_released:"):
                    key = data.split(b":")[1].decode().strip()
                    print(f"Client {addr} released key {key}")
                    conn.sendall(b"KEY RECIEVED")
                    if self.callback:
                        self.callback(key, "key")


                else:
                    print(f"Received: {data} from {addr}")
                    conn.sendall(b"OK")


            except ConnectionResetError:
                break

        print(f"Client {addr} disconnected")
        with self.lock:
            self.clients.remove(conn)

            if self.callback:
                self.callback(addr[0], "ip-remove")


    def stop(self):
        # Close the socket
        self.socket.close()
