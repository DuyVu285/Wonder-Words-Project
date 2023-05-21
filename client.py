import webbrowser
import socketio
import subprocess

sio = socketio.Client()

# Store the web browser process
browser_process = None


@sio.on("connect")
def handle_connect():
    print("Connected to the server")
    # Open home.html in a web browser
    global browser_process
    browser_process = subprocess.Popen(["webbrowser", "http://localhost:5000"])


@sio.on("disconnect")
def handle_disconnect():
    print("Disconnected from the server")
    # Close the web browser
    global browser_process
    if browser_process:
        browser_process.kill()


sio.connect("http://localhost:5000")

# Disconnect the client
while True:
    user_input = input("Type 'quit' to disconnect: ")
    if user_input.lower() == "quit":
        sio.disconnect()
        break
