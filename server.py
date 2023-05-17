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


    # To start the server call this function
    def start(self):
        # Bind socket to IP and port
        self.socket.bind((self.ip, self.port))

        # And run the server
        self.run()

    # The main server function, handling the server and not letting it die
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

            # A client has connected, first check if the server is full
            if len(self.clients) < self.max_clients:

                # If not, let the main script know by sending the ip back through the callback function
                self.clients.append(conn)
                if self.callback:
                    self.callback(addr[0], "ip-add")

                # And start a new thread for listening to what the client sends (the key inputs)
                thread = threading.Thread(target=self.listen_to_client, args=(conn, addr))
                thread.start()
            else:
                conn.sendall(b"Server is full")
                conn.close()

        # Close all client sockets (if an OSError occurs)
        with self.lock:
            for conn in self.clients:
                conn.close()

    # This method will just send and recieve messages from the clients, to verify their status, also recieve the key inputss
    def listen_to_client(self, conn, addr):
        print(f"Connected by {addr}")
        with self.lock:
            self.clients.append(conn)

        while True:
            try:
                # Try to recieve data from the client, if data comes, it will continue down the script
                data = conn.recv(1024)
                if not data:
                    break

                # Check what type of data is sent by the client
                # If its a key pressed down event
                if data.startswith(b"key:"):
                    key = data.split(b":")[1].decode().strip()
                    print(f"Client {addr} pressed key {key}")
                    conn.sendall(b"KEY RECIEVED")
                    if self.callback:
                        self.callback(key, "key")
                
                # -- or if its a key released event
                elif data.startswith(b"key_released:"):
                    key = data.split(b":")[1].decode().strip()
                    print(f"Client {addr} released key {key}")
                    conn.sendall(b"KEY RECIEVED")
                    if self.callback:
                        self.callback(key, "key_released")

                # -- if not just print it out and send back an OK
                else:
                    print(f"Received: {data} from {addr}")
                    conn.sendall(b"OK")


            except ConnectionResetError:
                break

        # If the client breaks the connection, it will be printed out
        print(f"Client {addr} disconnected")
        with self.lock:

            # Remove the client from the clients_connected array
            self.clients.remove(conn)

            # And then update the main script by sending an "ip-remove" request, to get it to remove the client from the GUI
            if self.callback:
                self.callback(addr[0], "ip-remove")


    def stop(self):
        # Close the socket
        self.socket.close()
