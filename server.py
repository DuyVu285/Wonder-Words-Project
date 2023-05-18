import json
import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

words = []
word = ""
unrevealed_word = ""
players = {}


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
    player_id = request.sid
    if player_id not in players:
        players[player_id] = {"name": None, "score": 0}
        emit("prompt_register_name", room=player_id)
    emit("update", get_game_data(player_id), room=player_id)
    emit(
        "update_players", get_players_data(), room=player_id
    )  # Send player list to the newly connected player only


@socketio.on("register_name")
def register_name(data):
    player_id = request.sid
    players[player_id]["name"] = data["name"]
    emit("update_players", get_players_data(), broadcast=True)


@socketio.on("guess")
def handle_guess_event(data):
    global word
    global unrevealed_word

    player_id = request.sid
    player_data = players.get(player_id, {})
    if player_data.get("name") is None:
        emit("update", get_game_data(player_id), room=player_id)
        return

    guess = data["guess"].strip().lower()
    if guess == "ready":
        print("Player is ready")
        return

    unrevealed_word, is_correct = handle_guess(
        guess, word["word_entry"], unrevealed_word
    )

    if is_correct:
        score_multiplier = 100 * word["word_entry"].lower().count(guess)
        player_data["score"] += score_multiplier
        emit("update_players", get_players_data(), broadcast=True)
    else:
        emit("wrong", room=player_id)

    if "-" not in unrevealed_word:
        print(f"Word revealed: {word}")
        emit("win", room=player_id)

    emit("update", get_game_data(player_id), broadcast=True)


def get_game_data(player_id):
    return {
        "unrevealed_word": unrevealed_word,
        "is_correct": None,
        "score": players.get(player_id, {}).get("score", 0),
        "desc": word["description"],
    }


def get_players_data():
    return {
        "player_names": [player["name"] for player in players.values()],
        "player_scores": [player["score"] for player in players.values()],
    }


if __name__ == "__main__":
    words = load_words()
    word = select_word(words)
    unrevealed_word = generate_unrevealed_word(word)

    socketio.run(app, debug=True)
