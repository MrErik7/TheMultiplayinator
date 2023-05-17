# Libraries for building the GUI
import sys  
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QGridLayout, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5 import QtGui

# Own-made libraries
from client import *
from server import *

import keyboard # The keyboard module is used to press down the keys recieved from the client (note that this requires *root access on linux)
import socket # The socket module is simply used to retrieve the users ip, not any server or client handling

# The main class of this program, a class part of the GUI module (pyqt5)
class MyWindow(QWidget):

    # Initializement of the module 
    def __init__(self):
        super().__init__()
        self.initUI()

    # Initializement of the GUI 
    def initUI(self):
        self.setWindowTitle('The Multiplayinator')
        self.setWindowIcon(QtGui.QIcon("img/logo.png"))

        # Set variables
        self.window_running = True 
        self.key_input_activated = False

        # Create a layout
        layout = QGridLayout()

        # Create the labels
        self.lblWelcome = QLabel('Welcome to the official multiplayinator, start a server or connect to an existing. \n Your IP: ' + socket.gethostbyname(socket.gethostname()), self)
        self.lblResponse = QLabel('-Response-', self)
        self.lblKey = QLabel('Key input activated: ' + str(self.key_input_activated), self)
        self.lblClients = QLabel('Connected clients: ', self)

        # Display the welcome and response label
        self.lblResponse.setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.lblWelcome, 0, 0, 1, 2)
        layout.addWidget(self.lblResponse, 1, 0, 1, 2)

        # Create the label dividers
        self.lblServerDiv = QLabel('Server:')
        self.lblClientDiv = QLabel('Client:')

        # Center the server and client label horizontally
        self.lblServerDiv.setAlignment(Qt.AlignHCenter)
        self.lblClientDiv.setAlignment(Qt.AlignHCenter)        

        # Add the label dividers to the widget
        layout.addWidget(self.lblServerDiv, 3, 0)
        layout.addWidget(self.lblClientDiv, 3, 1)

        # Add the key input and connected clients labels
        layout.addWidget(self.lblKey, 4, 0)
        layout.addWidget(self.lblClients, 5, 0)

        # Create the host server button
        self.btnServer = QPushButton('Host Server', self)
        self.btnServer.clicked.connect(self.host_server)
        layout.addWidget(self.btnServer, 6, 0)

        # Create the shutdown server button
        self.btnShutdownServer = QPushButton('Shutdown Server', self)
        self.btnShutdownServer.clicked.connect(self.shutdown_server)
        layout.addWidget(self.btnShutdownServer, 7, 0)

        # Create the toggle key activation 
        self.btnToggleKeys = QPushButton('Toggle key input', self)
        self.btnToggleKeys.clicked.connect(self.toggle_key_input)
        layout.addWidget(self.btnToggleKeys, 8, 0)

        # Create the connect to server button
        self.btnConnect = QPushButton('Connect to Server', self)
        self.btnConnect.clicked.connect(self.connect_to_server)
        layout.addWidget(self.btnConnect, 6, 1)

        # Create the leave server button
        self.btnLeaveServer = QPushButton('Leave Server', self)
        self.btnLeaveServer.clicked.connect(self.leave_server)
        layout.addWidget(self.btnLeaveServer, 7, 1)

        # Create a line edit for the IP input
        self.input_ip = QLineEdit(self)
        self.input_ip.setPlaceholderText("Enter IP adress...")

        # Create a line edit for the port input
        self.input_port = QLineEdit(self)
        self.input_port.setPlaceholderText("Enter port...")

        # Add the widgets
        layout.addWidget(self.input_port, 9, 0)
        layout.addWidget(self.input_ip, 9, 1)

        # Set the layout for the window
        self.setLayout(layout)

        # Set the size of the window to 400x300 pixels
        self.setGeometry(100, 100, 400, 300)

    # The main method for hosting a server, linked to the "host server" button
    def host_server(self):
        # Get the text from the input box
        port = self.input_port.text()

        # Setup the server
        self.server_thread = ServerThread(port, self.key_input_activated)
        self.server_thread.response_signal.connect(self.update_response_label)
        self.server_thread.label_client_signal.connect(self.update_clients_label)

        # Start the server thread
        self.server_thread.start()
        self.lblResponse.setText("Waiting for connections...")
     
    # The main method for connecting to a server, linked to the "connect to server" button
    def connect_to_server(self):
        # Get the text from the input box
        ip = self.input_ip.text()
        port = self.input_port.text()

        # Setup the client thread
        self.client_thread = ClientThread(ip, port)
        self.client_thread.response_signal.connect(self.update_response_label)
        
        # Start the client thread
        self.client_thread.start()

    # The main method for shutting down a server, linked to the "shutdown server" button
    def shutdown_server(self):
        try:
            self.server_thread.stop()
        
        except AttributeError:
            self.lblResponse.setText("Server must be started to be able to shutdown.") 

    # The method for leaving a server
    def leave_server(self):
        self.client_thread.leave_server()

    
    # The method for toggle the key input button, linked to the "toggle key input" button
    def toggle_key_input(self):
        # Change the condition of the key input activated variable
        self.key_input_activated = not self.key_input_activated

        # Then update the visual part
        self.lblKey.setText('Key input activated: ' + str(self.key_input_activated))

        # Then try to, if the server is running, to change the condition in the server thread
        try:
            self.server_thread.toggle_key_input(self.key_input_activated)

        except AttributeError:
            print("Server must be running in order to change the server thread. ")
            

    # The method to update the response label, this is called from inside the server and client threads
    def update_response_label(self, response):
        self.lblResponse.setText(response)

    # The method to update the clients label, this is called from inside the server thread
    def update_clients_label(self, client_list):
        self.lblClients.setText('Connected clients: \n' + client_list)

# Note from the developer:
# Using a class here has its pros and cons, 
# pros: Since its a thread, the rest of the program can be runned without it freezing 
# cons: Accessing the label in the main class is a bit tricky and is done by emiting signals, unneccesary code if i skipped the class
# However, the pros outweigh the cons in this case.
# Same is with the client thread.
# The main thread that starts when a user starts a server.   
class ServerThread(QThread):
    # Initialize the label signals, simply put it: pyqtsignals are developed by pyt5 to make it possible to update labels amongst classes
    response_signal = pyqtSignal(str)
    label_client_signal = pyqtSignal(str)

    # Initialize the server thread
    def __init__(self, port, key_condition):
        super().__init__()
        self.port = port
        self.connected_clients = []
        self.key_input = key_condition

    # The main method of the server thread, initialzing the Server from the server script
    def run(self):
        try:
            self.server = Server(int(self.port))
        except ValueError:

            # If the user doesnt fill in the port, it will raise an ValueError
            self.response_signal.emit('Port needs to be filled in.')
            return

        # Set the variables and the callback function
        self.server_running = True
        self.server.set_callback(self.handle_callback)

        # And upate the response label
        self.response_signal.emit('Server started.')

        # While the variable, server_running is true, keep the server going
        while self.server_running:
            self.server.start()

        # Otherwise if the server is stopped, displayed this with the response label
        self.response_signal.emit('Server closed.')

     # The function to stop the server, called when the owner of the server decides to press the shutdown server button   
    def stop(self):
        self.server_running = False
        self.server.stop()
        self.response_signal.emit('Server closed.')
        self.label_client_signal.emit('')

    # This function handles the callback, the signals sent from the server script, (keys and if clients join or leave)
    def handle_callback(self, value, type):
        if (type == "key"):
            # First check if key input is activated, or else it wont press
            if self.key_input:
                try:
                    # And then press the key provided
                    keyboard.press(str(value))
                except ValueError:
                    print("Key is not valid, server won't press.")
            else:
                print("Key input is not activated.")


        elif type == "key_released":
            # First check if key input is activated, or else it wont press
            if self.key_input:
                try:
                    # And then release the key provided
                    keyboard.release(str(value))
                except ValueError:
                    print("Key is not pressed down.")
            else:
                print("Key input is not activated.")


        elif (type == "ip-add"):
            self.connected_clients.append(value)
            self.label_client_signal.emit(str(self.connected_clients)[1:-1])

        elif (type == "ip-remove"):
            self.connected_clients.remove(value)
            self.label_client_signal.emit(str(self.connected_clients)[1:-1])

    # And if the key input is updated, while the server is running, the condition inside the serverthread must be changed aswell
    def toggle_key_input(self, condition):
        self.key_input = condition

# The main thread that starts when a user joins a server, becomes a client.  
class ClientThread(QThread):
    # Initialize the label signals
    response_signal = pyqtSignal(str)

    # Initialize the client thread, the ip and port are of intrest. Also self.client is to check wether the client is connected or not. 
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        self.client = None

    # Once the run function is called the client will try to connect to the server
    def run(self):
        # Try and connect to the server
        self.client = Client(self.ip, self.port)
        self.client.set_callback(self.handle_callback)
        self.client.connect()
        self.response_signal.emit('Connected to ' + str(self.ip) + " on port " + str(self.port))

    # A function to handle the callback from the client script, in this case being the server status, if its connected or not
    def handle_callback(self, value):
        if value == "closed":
            self.response_signal.emit('Disconnected, server was closed.')

    # A function called when the user wants to leave a server. 
    def leave_server(self):
        if self.client:
            self.client.leave_server()
            self.response_signal.emit('Disconnected.')

# And then the code to initialize the main GUI class, once the program is started
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
