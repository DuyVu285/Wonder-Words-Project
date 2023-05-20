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
turn = 0
ready_statuses = {}


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
    ready_statuses[player_id] = False
    emit("update_ready_players", get_players_ready_data(), broadcast=True)


# Ready
@socketio.on("ready")
def ready():
    player_id = request.sid
    ready_statuses[player_id] = True
    emit("update_ready_players", get_players_ready_data(), broadcast=True)

    # Check if all players are ready
    if len(ready_statuses) >= 2 and all(ready for ready in ready_statuses.values()):
        emit("start_timer", get_players_data(), broadcast=True)
        ready_statuses.clear()


@socketio.on("guess")
def handle_guess_event(data):
    global word
    global unrevealed_word
    global turn

    player_id = request.sid
    player_data = players.get(player_id, {})

    # Check if the player is the current turn player
    if player_data.get("name") == registration_order[0]:
        turn = turn + 1
        guess = data["guess"].strip().lower()
        unrevealed_word, is_correct = handle_guess(
            guess, word["word_entry"], unrevealed_word
        )

        if "-" not in unrevealed_word:
            print(f"Word revealed: {word}")
            emit("win", get_players_data, broadcast=True)

        if is_correct:
            score_multiplier = 100 * word["word_entry"].lower().count(guess)
            player_data["score"] += score_multiplier
            emit("right", get_players_data(), room=player_id)
        else:
            emit("wrong", get_players_data(), broadcast=True)
            handle_switch_player()

        emit("update_turn", get_players_data(), broadcast=True)


@socketio.on("switch_player")
def handle_switch_player():
    global registration_order
    global turn
    turn = turn + 1
    registration_order.append(registration_order.pop(0))
    emit("update_turn", get_players_data(), broadcast=True)


def get_players_ready_data():
    return {
        "player_names": [player["name"] for player in players.values()],
        "ready_statuses": [
            ready_statuses.get(player_id, False) for player_id in players.keys()
        ],
    }


def get_players_data():
    player_scores = [player["score"] for player in players.values()]
    max_score = max(player_scores)
    winning_players = [
        player["name"] for player in players.values() if player["score"] == max_score
    ]
    losing_players = [
        player["name"] for player in players.values() if player["score"] != max_score
    ]

    return {
        "unrevealed_word": unrevealed_word,
        "desc": word["description"],
        "player_names": [player["name"] for player in players.values()],
        "player_scores": player_scores,
        "order": registration_order,
        "turn": turn,
        "winning_players": winning_players,
        "losing_players": losing_players,
    }


if __name__ == "__main__":
    words = load_words()
    word = select_word(words)
    unrevealed_word = generate_unrevealed_word(word)

    socketio.run(app, debug=True)
