import sys
import keyboard
import socket # The socket module is simply used to retrieve the users ip, not any server or client handling
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QGridLayout, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5 import QtGui
from client import *
from server import *

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

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

        self.lblResponse.setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.lblWelcome, 0, 0, 1, 2)
        layout.addWidget(self.lblResponse, 1, 0, 1, 2)

        # Create the label dividers
        self.lblServerDiv = QLabel('Server:')
        self.lblClientDiv = QLabel('Client:')

        # Center the server and client label horizontally
        self.lblServerDiv.setAlignment(Qt.AlignHCenter)
        self.lblClientDiv.setAlignment(Qt.AlignHCenter)        

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
     
    def connect_to_server(self):
        # Get the text from the input box
        ip = self.input_ip.text()
        port = self.input_port.text()

        # Setup the client thread
        self.client_thread = ClientThread(ip, port)
        self.client_thread.response_signal.connect(self.update_response_label)
        
        # Start the client thread
        self.client_thread.start()


    def shutdown_server(self):
        try:
            self.server_thread.stop()
        
        except AttributeError:
            self.lblResponse.setText("Server must be started to be able to shutdown.") 

    def leave_server(self):
        self.client_thread.leave_server()

    
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
            

    def update_response_label(self, response):
        self.lblResponse.setText(response)

    def update_clients_label(self, client_list):
        self.lblClients.setText('Connected clients: \n' + client_list)

# Note from the developer:
# Using a class here has its pros and cons, 
# pros: Since its a thread, the rest of the program can be runned without it freezing 
# cons: Accessing the label in the main class is a bit tricky and is done by emiting signals, unneccesary code if i skipped the class
# However, the pros outweigh the cons in this case.
# Same is with the client thread. 
class ServerThread(QThread):
    response_signal = pyqtSignal(str)
    label_client_signal = pyqtSignal(str)

    def __init__(self, port, key_condition):
        super().__init__()
        self.port = port
        self.connected_clients = []
        self.key_input = key_condition

    def run(self):
        self.server = Server(int(self.port))
        self.server_running = True
        self.server.set_callback(self.handle_callback)

        self.response_signal.emit('Server started.')

        while self.server_running:
            self.server.start()

        self.response_signal.emit('Server closed.')
        
    def stop(self):
        self.server_running = False
        self.server.stop()
        self.response_signal.emit('Server closed.')
        self.label_client_signal.emit('')

    def handle_callback(self, value, type):
        # Release all previously pressed keys

        if (type == "key"):
            # First check if key input is activated, or else it wont press
            if self.key_input:
                try:
                    keyboard.press(str(value))
                except ValueError:
                    print("Key is not valid, server won't press.")
            else:
                print("Key input is not activated.")


        elif type == "key_released":
            if self.key_input:
                try:
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

    def toggle_key_input(self, condition):
        self.key_input = condition

class ClientThread(QThread):
    response_signal = pyqtSignal(str)

    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        self.client = None

    def run(self):
        # Try and connect to the server
        self.client = Client(self.ip, self.port)
        self.client.set_callback(self.handle_callback)
        self.client.connect()
        self.response_signal.emit('Connected to ' + str(self.ip) + " on port " + str(self.port))

    def handle_callback(self, value):
        if value == "closed":
            self.response_signal.emit('Disconnected, server was closed.')

    def leave_server(self):
        if self.client:
            self.client.leave_server()
            self.response_signal.emit('Disconnected.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
