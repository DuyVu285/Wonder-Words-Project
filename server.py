import json
import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

player_scores = {}
word = ""
unrevealed_word = ""
player_name = ""

def load_words():
    with open("word_list.json") as f:
        words = json.load(f)
    return words

def select_word(words):
    return random.choice(words)

def generate_unrevealed_word(word_slice):
    word = word_slice["word_entry"]
    return "".join(["-" if c != " " else " " for c in word])

def handle_guess(guess, word, unrevealed_word):
    guess_lower = guess.lower()
    word_lower = word.lower()
    new_unrevealed_word = unrevealed_word

    if guess_lower in word_lower:
        for i, c in enumerate(word_lower):
            if c == guess_lower:
                new_unrevealed_word = (
                    new_unrevealed_word[:i] + word[i] + new_unrevealed_word[i + 1 :]
                )
        return new_unrevealed_word, True
    else:
        return new_unrevealed_word, False

@app.route("/home")
def home_page():
    return render_template("home.html")

@app.route("/start_game")
def start_game_route():
    return render_template("game.html", player_name=player_name)

@socketio.on("start_game")
def start_game(data):
    global player_name
    player_name = data["player_name"]
    socketio.emit("redirect", "/start_game")

@socketio.on("connect")
def handle_connect():
    player_scores[request.sid] = 0
    print("A player connected")

    emit(
        "update",
        {
            "unrevealed_word": unrevealed_word,
            "is_correct": None,
            "score": player_scores[request.sid],
            "desc": word["description"],
            "player_name": player_name,
        },
        room=request.sid,
    )


@socketio.on("guess")
def handle_guess_event(data):
    global word
    global unrevealed_word

    guess = data["guess"].strip().lower()
    if guess == "ready":
        print("Player is ready")
        return

    unrevealed_word, is_correct = handle_guess(
        guess, word["word_entry"], unrevealed_word
    )

    score_multiplier = 0
    if is_correct:
        score_multiplier = 100 * word["word_entry"].lower().count(guess)
        player_scores[request.sid] += score_multiplier

    if not is_correct:
        socketio.emit("wrong", room=request.sid)

    if "-" not in unrevealed_word:
        print(f"Word revealed: {word}")
        socketio.emit("win", room=request.sid)

    emit(
        "update",
        {
            "unrevealed_word": unrevealed_word,
            "is_correct": is_correct,
            "score": player_scores[request.sid],
            "desc": word["description"],
            "player_name": player_name,
        },
    )
    print("score", player_scores)
    print(player_scores[request.sid])


if __name__ == "__main__":
    words = load_words()
    word = select_word(words)
    unrevealed_word = generate_unrevealed_word(word)

    socketio.run(app, debug=True)
