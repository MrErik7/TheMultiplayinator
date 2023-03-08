import socket
 
def server(ip, port):
    # Create a server socket
    serverSocket = socket.socket()

    # Bind the server to the IP and port
    serverSocket.bind((ip, port))
    print("Server socket bound with with ip {} port {}".format(ip, port))

    # Make the server listen for incoming connections
    serverSocket.listen()

    # Start the server loop
    while(True):
        print("Now listening...\n")
        (clientConnection, clientAddress) = serverSocket.accept()
        print("Client has connected with IP " + str(clientAddress))
        data = clientConnection.recv(1024)

        if not data:
            break
        elif data == 'killsrv':
            clientConnection.close()
        
        elif data == "hello":
            msg1  = "Hi Client! Read everything you sent"
            msg1Bytes = str.encode(msg1) 
            clientConnection.send(msg1Bytes)          



        else:
            print(data)


    


server("", 35491)