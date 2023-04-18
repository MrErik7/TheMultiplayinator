import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal
from client import *
from server import *

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PI Multiplayer Machine')

        # Set variables
        self.window_running = True 

        # Create a layout
        layout = QVBoxLayout()

        # Create a label
        self.lblWelcome = QLabel('Welcome to the PI Multiplayer Machine.', self)
        self.lblResponse = QLabel('-Response-', self)

        layout.addWidget(self.lblWelcome)
        layout.addWidget(self.lblResponse)

        # Create the host server button
        self.btnServer = QPushButton('Host Server', self)
        self.btnServer.clicked.connect(self.host_server)
        layout.addWidget(self.btnServer)

        # Create the shutdown server button
        self.btnShutdownServer = QPushButton('Shutdown Server', self)
        self.btnShutdownServer.clicked.connect(self.shutdown_server)
        layout.addWidget(self.btnShutdownServer)

        # Create the connect to server button
        self.btnConnect = QPushButton('Connect to Server', self)
        self.btnConnect.clicked.connect(self.connect_to_server)
        layout.addWidget(self.btnConnect)
 
        # Create a line edit for user input
        self.input_ip = QLineEdit(self)
        self.input_port = QLineEdit(self)

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
        self.server_thread = ServerThread(port)
        self.server_thread.response_signal.connect(self.update_response_label)

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
        self.server_thread.stop()


    def update_response_label(self, response):
        self.lblResponse.setText(response)



class ServerThread(QThread):
    response_signal = pyqtSignal(str)

    def __init__(self, port):
        super().__init__()
        self.port = port

    def run(self):
        self.server = Server(int(self.port))
        self.server_running = True

        while self.server_running:
            self.server.start()
        
        self.response_signal.emit('Server closed.')
        
    def stop(self):
        self.server_running = False
        self.server.stop()
        self.response_signal.emit('Server closed.')

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
