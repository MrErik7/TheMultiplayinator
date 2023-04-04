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

        # Await clients to connect
        while self.server_running:
            try:
                # Await clients to connect
                while self.server_running:
                    connected = False
                    while not connected:
                        connected = self.server.await_connections()

                # When a client has been connected --> start listening for data from the clients
                while self.server_running:
                    print("running")
                    response_bytes = self.server.listen()

                    # Check so the response is actually bytes before decoding
                    if response_bytes.__class__ == bytes:
                        response_str = response_bytes.decode('utf-8')

                    self.response_signal.emit("Message recieved: " + response_str)

            except ConnectionError:
                self.response_signal.emit('Lost connection to client, connection cancelled. Server still running...')
                break 

    def stop(self):
        self.server_running = False
        self.server.shutdown()
        self.response_signal.emit('Server closed.')


class ClientThread(QThread):
    response_signal = pyqtSignal(str)

    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port

    def run(self):
        # Try and connect to the server
        client = Client()
        client.connect(self.ip, self.port)
        print("client connected")

        if (client.listen() == b"OK"):
            self.connected = True
            print("recieved ok")

        while self.connected:
            self.response_signal.emit('Connected to ' + str(self.p) + " on port " + str(self.port))
            
            try:
                response_str = client.listen().decode('utf-8')
                self.response_signal.emit(response_str)

            except ConnectionResetError:
                self.response_signal.emit('Lost connection to server, connection cancelled.')
                break          



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
