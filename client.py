import webbrowser
import socketio

sio = socketio.Client()


@sio.on("connect")
def handle_connect():
    print("Connected to the server")
    # Open home.html in a web browser
    webbrowser.open("http://localhost:5000")


@sio.on("disconnect")
def handle_disconnect():
    print("Disconnected from the server")
    return


sio.connect("http://localhost:5000")

# Disconnect the client
while True:
    user_input = input("Type 'quit' to disconnect: ")
    if user_input.lower() == "quit":
        sio.disconnect()
        break
