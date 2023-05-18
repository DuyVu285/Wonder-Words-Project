import webbrowser
import socketio

sio = socketio.Client()

@sio.on('connect')
def handle_connect():
    print('Connected to the server')
    # Open home.html in a web browser
    webbrowser.open('http://localhost:5000/home')

@sio.on('disconnect')
def handle_disconnect():
    print('Disconnected from the server')

sio.connect('http://localhost:5000')
