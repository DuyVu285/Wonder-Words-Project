import json
import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

player_scores = {}
word = ""
unrevealed_word = ""

def load_words():
    with open("word_list.json") as f:
        words = json.load(f)
    return words

def select_word(words):
    return random.choice(words)

def generate_unrevealed_word(word_slice):
    word = word_slice['word_entry']
    return "".join(["-" if c != " " else " " for c in word])

def handle_guess(guess, word, unrevealed_word):
    guess_lower = guess.lower()
    word_lower = word.lower()
    new_unrevealed_word = unrevealed_word

    if guess_lower in word_lower:
        for i, c in enumerate(word_lower):
            if c == guess_lower:
                new_unrevealed_word = new_unrevealed_word[:i] + word[i] + new_unrevealed_word[i + 1 :]
        return new_unrevealed_word, True
    else:
        return new_unrevealed_word, False



@app.route("/")
def game_page():
    return render_template("game.html")

@socketio.on("connect")
def handle_connect():
    global player_id
    player_id = request.sid
    player_scores[player_id] = 0
    print("A player connected")
    
    # Send initial game state to the connected player
    emit(
        "update",
        {
            "unrevealed_word": unrevealed_word,
            "is_correct": None,
            "score": None,
            "player_id": player_id,
        },
        room=player_id,
    )

@socketio.on("guess")
def handle_guess_event(data):
    global word
    global unrevealed_word
    
    guess = data["guess"].strip().lower()
    if guess == "ready":
        print("Player is ready")
        return

    unrevealed_word, is_correct = handle_guess(guess, word['word_entry'], unrevealed_word)

    score_multiplier = 0
    if is_correct:
        # Calculate the score
        score_multiplier = 100 * word['word_entry'].count(guess)
        player_scores[player_id] += score_multiplier

    if "-" not in unrevealed_word:
        print(f"Word revealed: {word}")
        # Handle game completion here

    # Send the updated game state to all players
    emit(
        "update",
        {
            "unrevealed_word": unrevealed_word,
            "is_correct": is_correct,
            "score": score_multiplier,
        },
    )

if __name__ == "__main__":
    words = load_words()
    word = select_word(words)
    unrevealed_word = generate_unrevealed_word(word)

    socketio.run(app, debug=True)
