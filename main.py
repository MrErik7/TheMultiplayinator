import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit
from client import *
from server import *

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PI Multiplayer Machine')

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
        server = Server(int(port))

        # Await clients to connect
        server.await_connections()

        # When a client has been connected --> start listening for data from the clients
        while True:
            try:
                self.lblResponse.setText(server.listen())

            except ConnectionResetError:
                self.lblResponse.setText('Lost connection to server, connection cancelled.')
                break          



    def connect_to_server(self):
        # Get the text from the input box
        ip = self.input_ip.text()
        port = self.input_port.text()

        # Try and connect to the server
        client = Client()
        client.connect(ip, port)

        if (client.listen() == b"OK"):
            self.lblResponse.setText('Connected to ' + str(ip) + " on port " + str(port))

        while True:
            try:
                self.lblResponse.setText(client.listen())

            except ConnectionResetError:
                self.lblResponse.setText('Lost connection to server, connection cancelled.')
                break          

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
