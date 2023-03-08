# echo-client.py
import socket


def connect(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(b"Hello")
        data = s.recv(1024)

    print(f"Received {data!r}")


connect("127.0.0.1", 35491)