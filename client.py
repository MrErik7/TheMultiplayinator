import socket
import threading
import keyboard

class Client:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.printable_keys = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ' ', ',', '.', '/', ';', '\'', '[', ']', '\\', '-', '=', '`', 'space']

    def connect(self):
        self.socket.connect((self.ip, int(self.port)))
        self.socket.sendall(b"Hello server")

        # Start the sending and receiving thread
        threading.Thread(target=self.start_communication).start()

    def start_communication(self):
        self.socket.sendall(b"Im alive")
        print("Message sent to server: Im alive")

        while True:
            try:                
                # Check for key press and send it to server
                event = keyboard.read_event()
                if event.event_type == "down" and event.name in self.printable_keys:
                    self.socket.sendall(("key:" + event.name).encode('utf-8'))
                
                elif event.event_type == "up" and event.name in self.printable_keys:
                    self.socket.sendall(("key_released:" + event.name).encode('utf-8'))


            except ConnectionResetError:
                print("Server disconnected")
                break
