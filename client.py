import socket
import threading
import keyboard

class Client:
    def __init__(self, ip, port):
        # Initialize the socket, also set the ip and port to (self) so it can be accessed in other functions
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port

        # The printable_keys array contains all the keys that will be sent to the server, all the acceptable keys. 
        self.printable_keys = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ' ', ',', '.', '/', ';', '\'', '[', ']', '\\', '-', '=', '`', 'space', 'down', 'up', 'left', 'right', 'uppil', 'vänsterpil', 'nedpil', 'högerpil']

        # Initialize callback function
        self.callback = None

    # This method sends back data, the state of the server, to the main script
    def set_callback(self, callback):
        self.callback = callback

    # A client doesnt connect to a server once initialized, this method is the "main" method of the client class and once called it will begin communication
    def connect(self):
        self.socket.connect((self.ip, int(self.port)))
        self.socket.sendall(b"Hello server")

        # Start the sending and receiving thread
        threading.Thread(target=self.start_communication).start()

    # The function that enables the communication between the server and the client
    def start_communication(self):
        
        # Send a greeting to the server, to yeah, let it know that its alive and well
        self.socket.sendall(b"Im alive")
        print("Message sent to server: Im alive")

        while True:
            try:                
                # Check for key press and send it to server
                event = keyboard.read_event()

                # Check for key "down" events, such as when a button is pressed
                if event.event_type == "down" and event.name in self.printable_keys:
                    self.socket.sendall(("key:" + event.name).encode('utf-8'))
                    
                # Check for key "up" events, such as when a button is released
                elif event.event_type == "up" and event.name in self.printable_keys:
                    self.socket.sendall(("key_released:" + event.name).encode('utf-8'))


            except ConnectionResetError:
                print("Server was closed")
                
                # Send back the status of the server to the main script
                if self.callback:
                    self.callback("closed")

                break

    # Self explanatory, closing the socket to the server when a client wants to leave
    def leave_server(self):
        self.socket.close()