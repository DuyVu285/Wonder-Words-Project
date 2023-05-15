import webbrowser
import socketio

sio = socketio.Client()

@sio.on('update')
def handle_update(data):
    unrevealed_word = data['unrevealed_word']
    is_correct = data['is_correct']
    score = data['score']

    print(f'Unrevealed word: {unrevealed_word}')
    if is_correct:
        print(f'Your guess is correct! Score: {score}')
    else:
        print('Your guess is incorrect.')

    print('------------------------------')

@sio.on('connect')
def handle_connect():
    print('Connected to the server')
    # Open home.html in a web browser
    webbrowser.open('http://localhost:5000')

@sio.on('disconnect')
def handle_disconnect():
    print('Disconnected from the server')

sio.connect('http://localhost:5000')

while True:
    guess = input('Enter your guess (or "ready" to start): ')

    sio.emit('guess', {'guess': guess})

    if guess.lower() == 'ready':
        print('Waiting for the game to start...')
        print('------------------------------')

sio.disconnect()
