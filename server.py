# echo-server.py
import socket
import json
import time

# for debug
import keyboard

class Server:
    def __init__(self):
        # Initialize socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Initialize server info
        self.ip = ""
        self.port = 14576

        # Initialize game state
        self.game_state = {
            "players": {
                "player1": {
                    "x": 0,
                    "y": 0,
                    "score": 0
                },
                "player2": {
                    "x": 10,
                    "y": 10,
                    "score": 0
                }
            }
        }

    def update_game_state(self, player_id, x, y, score):
        # Update the game state with the new player position and score
        self.game_state["players"][player_id]["x"] = x
        self.game_state["players"][player_id]["y"] = y
        self.game_state["players"][player_id]["score"] = score


    def send_game_state(self, conn):
        # Convert the game state to JSON
        game_state_json = json.dumps(self.game_state)

        # Send the game state to the client
        conn.sendall(game_state_json.encode())



    def start(self):
        # Bind socket to IP and port
        self.socket.bind((self.ip, self.port))

        # Listen for incoming connections
        self.socket.listen()

        while True:
            print("Waiting for connection...")
            conn, addr = self.socket.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    try:
                        data = conn.recv(1024)
                    except ConnectionResetError:
                        print("Client disconnected")
                        break
                    
                    if not data:
                        continue

                    print(f"Received: {data}")
                    conn.sendall(b"Message received")

                    # Now for the debugging part (remove this when script moves to retropie)
                    decoded_data = data.decode()
                    if "w" in decoded_data.lower():
                        keyboard.press('w')

                    if "a" in decoded_data.lower():
                        keyboard.press('a')

                    if "s" in decoded_data.lower():
                        keyboard.press('s')

                    if "d" in decoded_data.lower():
                        keyboard.press('d')

                    try:
                        keyboard.release(decoded_data)
                    except:
                        print("Canty release")



                    if (data == "quit"):
                        break



server = Server()
server.start()
