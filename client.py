import socket
import threading

class Client:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port

    def connect(self):
        self.socket.connect((self.ip, int(self.port)))
        self.socket.sendall(b"Hello server")

        # Start the sending and receiving thread
        threading.Thread(target=self.start_communication).start()

    def start_communication(self):
        while True:
            try:
                # Send a message to the server every 5 seconds
                self.socket.sendall(b"Im alive")
                print("Message sent to server: Im alive")

                # Wait for the response from the server
                data = self.socket.recv(1024)

                if not data:
                    continue
                else:
                    print(f"Message received from server: {data.decode('utf-8')}")

            except ConnectionResetError:
                print("Server disconnected")
                break

# Example usage
#client = Client("127.0.0.1", 3333)
#client.connect()
