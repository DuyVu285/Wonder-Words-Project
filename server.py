import json
import random
from flask import Flask, redirect, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

words = []
word = ""
unrevealed_word = ""
player_names = {}
player_scores = {}

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


@app.route("/")
def home():
    return render_template("game.html")


@socketio.on("connect")
def handle_connect():
    print("A player connected")
    
    emit(
        "update",
        {
            "unrevealed_word": unrevealed_word,
            "is_correct": None,
            "score": player_scores.get(request.sid, 0),
            "desc": word["description"],
            "player_name": player_names.get(request.sid),
        },
        room=request.sid,
    )

    update_players()


@socketio.on("register_name")
def register_name(data):
    player_names[request.sid] = data["name"]
    emit(
        "update",
        {
            "unrevealed_word": unrevealed_word,
            "is_correct": None,
            "score": player_scores.get(request.sid, 0),
            "desc": word["description"],
            "player_name": player_names.get(request.sid),
        },
        room=request.sid,
    )

    update_players()


@socketio.on("update")
def update(data):
    emit(
        "update",
        {
            "unrevealed_word": unrevealed_word,
            "is_correct": None,
            "score": player_scores.get(request.sid, 0),
            "desc": word["description"],
            "player_name": player_names.get(request.sid),
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
        player_scores[request.sid] = player_scores.get(request.sid, 0) + score_multiplier

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
            "score": player_scores.get(request.sid, 0),
            "desc": word["description"],
            "player_name": player_names.get(request.sid),
        },
    )

    update_players()


def update_players():
    for sid in list(player_scores.keys()):
        if sid not in player_names:
            del player_scores[sid]

    for sid in player_scores:
        emit(
            "update_players",
            {
                "player_names": list(player_names.values()),
                "player_scores": list(player_scores.values()),
            },
            room=sid,
        )


if __name__ == "__main__":
    words = load_words()
    word = select_word(words)
    unrevealed_word = generate_unrevealed_word(word)

    socketio.run(app, debug=True)
