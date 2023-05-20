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
registration_order = []
ready_players = 0
turn = 0


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
    new_unrevealed_word = unrevealed_word

    if guess_lower in word.lower():
        for i, c in enumerate(word):
            if c.lower() == guess_lower:
                new_unrevealed_word = (
                    new_unrevealed_word[:i] + c + new_unrevealed_word[i + 1 :]
                )
        return new_unrevealed_word, True

    return new_unrevealed_word, False


@app.route("/")
def home():
    return render_template("game.html")


@socketio.on("connect")
def handle_connect():
    print("Client ID: ", request.sid, " connected")


# Get player name
@socketio.on("register_name")
def register_name(data):
    player_id = request.sid
    if player_id not in players:
        players[player_id] = {"name": None, "score": 0}
    players[player_id]["name"] = data["name"]
    registration_order.append(data["name"])
    emit("update_ready_players", get_players_ready_data(), broadcast=True)


def get_players_ready_data():
    return {
        "player_names": [player["name"] for player in players.values()],
    }


# Ready
@socketio.on("ready")
def ready():
    global ready_players
    ready_players += 1
    if ready_players >= 2 and ready_players == len(players):
        emit("start_timer", {"players_data": get_players_data()}, broadcast=True)
        ready_players = 0


def get_players_data():
    return {
        "unrevealed_word": unrevealed_word,
        "desc": word["description"],
        "player_names": [player["name"] for player in players.values()],
        "player_scores": [player["score"] for player in players.values()],
        "order": registration_order,
        "turn": turn,
    }


@socketio.on("guess")
def handle_guess_event(data):
    global word
    global unrevealed_word
    global turn

    player_id = request.sid
    player_data = players.get(player_id, {})

    # Check if the player is the current turn player
    if player_data.get("name") == registration_order[0]:
        guess = data["guess"].strip().lower()
        unrevealed_word, is_correct = handle_guess(
            guess, word["word_entry"], unrevealed_word
        )

        if "-" not in unrevealed_word:
            print(f"Word revealed: {word}")
            emit("win", room=player_id)

        if is_correct:
            score_multiplier = 100 * word["word_entry"].lower().count(guess)
            player_data["score"] += score_multiplier
            emit("update", get_game_data(player_id), room=player_id)
        else:
            registration_order.append(registration_order.pop(0))
            emit("wrong", room=player_id)

        emit("update_game_state", get_players_data(), broadcast=True)
        turn = turn + 1
        emit("update_turn", get_players_data(), broadcast=True)
    else:
        emit("not_turn", room=player_id)


def get_game_data(player_id):
    return {
        "unrevealed_word": unrevealed_word,
        "score": players.get(player_id, {}).get("score", 0),
        "turn": turn,
        "order": registration_order,
    }


if __name__ == "__main__":
    words = load_words()
    word = select_word(words)
    unrevealed_word = generate_unrevealed_word(word)

    socketio.run(app, debug=True)
