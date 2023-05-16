import sys
import keyboard
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit
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
        layout = QVBoxLayout()

        # Create the labels
        self.lblWelcome = QLabel('Welcome to the official multiplayinator, start a server or connect to an existing. ', self)
        self.lblResponse = QLabel('-Response-', self)
        self.lblKey = QLabel('Key input activated: ' + str(self.key_input_activated), self)
        self.lblClients = QLabel('Connected clients: ', self)

        layout.addWidget(self.lblWelcome)
        layout.addWidget(self.lblResponse)
        layout.addWidget(self.lblKey)
        layout.addWidget(self.lblClients)

        # Create the label dividers
        self.lblServerDiv = QLabel('Server:')
        self.lblClientDiv = QLabel('Client:')

        # Center the server and client label horizontally
        self.lblServerDiv.setAlignment(Qt.AlignHCenter)
        self.lblClientDiv.setAlignment(Qt.AlignHCenter)        

        # Create the host server button
        self.btnServer = QPushButton('Host Server', self)
        self.btnServer.clicked.connect(self.host_server)
        layout.addWidget(self.btnServer)

        # Create the shutdown server button
        self.btnShutdownServer = QPushButton('Shutdown Server', self)
        self.btnShutdownServer.clicked.connect(self.shutdown_server)
        layout.addWidget(self.btnShutdownServer)

        # Create the toggle key activation 
        self.btnToggleKeys = QPushButton('Toggle key input', self)
        self.btnToggleKeys.clicked.connect(self.toggle_key_input)
        layout.addWidget(self.btnToggleKeys)

        # Create the connect to server button
        self.btnConnect = QPushButton('Connect to Server', self)
        self.btnConnect.clicked.connect(self.connect_to_server)
        layout.addWidget(self.btnConnect)

 
        # Create a line edit for user input
        self.input_ip = QLineEdit(self)
        self.input_ip.setPlaceholderText("Enter IP adress... (leave blank for server hosting)")

        self.input_port = QLineEdit(self)
        self.input_port.setPlaceholderText("Enter port...")

        layout.addWidget(self.input_ip)
        layout.addWidget(self.input_port)

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

    def handle_callback(self, value, type):

        if (type == "key"):

            # First check if key input is activated, or else it wont press
            if (self.key_input):
                try:
                    keyboard.press(str(value))
                except ValueError:
                    print("Key is not valid, server wont press. ")
            else:
                print("Key input is not activated. ")

        elif (type == "key_released"):
                
            # First check if key input is activated, or else it wont release
            if (self.key_input):
                try:
                    keyboard.release(str(value))
                except ValueError:
                    print("Key is not pressed down. ")
            else:
                print("Key input is not activated. ")

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

    def run(self):
        # Try and connect to the server
        client = Client(self.ip, self.port)
        client.connect() 
        self.response_signal.emit('Connected to ' + str(self.ip) + " on port " + str(self.port))

    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
