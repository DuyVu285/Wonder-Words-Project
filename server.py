import json
import random
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

WORD_LIST_FILE = "word_list.json"


class GameState:
    def __init__(self):
        self.words = []
        self.word = {}
        self.unrevealed_word = ""
        self.players = {}
        self.registration_order = []
        self.turn = 0
        self.ready_statuses = {}
        self.guessed_chars = set()


game_state = GameState()


def load_words():
    with open(WORD_LIST_FILE) as f:
        return json.load(f)


def select_word(words):
    return random.choice(words)


def generate_unrevealed_word(word_entry):
    word = word_entry["word_entry"]
    return "".join(["-" if c != " " else " " for c in word])


def handle_guess(guess, word, unrevealed_word):
    guess_lower = guess.lower()
    new_unrevealed_word = list(unrevealed_word)
    found = False

    for i, c in enumerate(word):
        if c.lower() == guess_lower:
            new_unrevealed_word[i] = c
            found = True

    return "".join(new_unrevealed_word), found


@app.route("/")
def home():
    return render_template("game.html")


@socketio.on("connect")
def handle_connect():
    player_id = request.sid
    print(f"Client ID: {player_id} connected")

    emit("update_ready_players", get_players_ready_data(), room=player_id)


@socketio.on("register_name")
def register_name(data):
    player_id = request.sid
    if player_id not in game_state.players:
        game_state.players[player_id] = {"name": data["name"], "score": 0}
        game_state.registration_order.append(data["name"])
        game_state.ready_statuses[player_id] = False

    emit("update_ready_players", get_players_ready_data(), broadcast=True)


@socketio.on("ready")
def ready():
    player_id = request.sid
    game_state.ready_statuses[player_id] = True
    emit("update_ready_players", get_players_ready_data(), broadcast=True)

    if len(game_state.ready_statuses) >= 2 and all(game_state.ready_statuses.values()):
        emit("start_timer", get_players_data(), broadcast=True)
        game_state.ready_statuses.clear()
        game_state.guessed_chars.clear()


@socketio.on("guess")
def handle_guess_event(data):
    player_id = request.sid
    player_data = game_state.players.get(player_id, {})

    if player_data.get("name") == game_state.registration_order[0]:
        guess = data["guess"].strip().lower()

        if guess in game_state.guessed_chars:
            emit("already_guessed", {"message": f"'{guess}' has already been guessed!"}, room=player_id)
            return

        game_state.guessed_chars.add(guess)  
        game_state.turn += 1

        game_state.unrevealed_word, is_correct = handle_guess(
            guess, game_state.word["word_entry"], game_state.unrevealed_word
        )

        if is_correct:
            score_multiplier = 100 * game_state.word["word_entry"].lower().count(guess)
            player_data["score"] += score_multiplier
            emit("right", room=player_id)
        else:
            emit("wrong", get_players_data(), broadcast=True)
            handle_switch_player()

        emit("update_turn", get_players_data(), broadcast=True)

        if "-" not in game_state.unrevealed_word:
            emit("win", get_players_data(), broadcast=True)


@socketio.on("switch_player")
def handle_switch_player():
    game_state.registration_order.append(game_state.registration_order.pop(0))
    emit("update_turn", get_players_data(), broadcast=True)


def get_players_ready_data():
    return {
        "player_names": [player["name"] for player in game_state.players.values()],
        "ready_statuses": [
            game_state.ready_statuses.get(player_id, False)
            for player_id in game_state.players.keys()
        ],
    }


def get_players_data():
    player_scores = [player["score"] for player in game_state.players.values()]
    max_score = max(player_scores, default=0)

    return {
        "unrevealed_word": game_state.unrevealed_word,
        "desc": game_state.word["description"],
        "player_names": [player["name"] for player in game_state.players.values()],
        "player_scores": player_scores,
        "order": game_state.registration_order,
        "turn": game_state.turn,
        "winning_players": [
            player["name"] for player in game_state.players.values() if player["score"] == max_score
        ],
        "losing_players": [
            player["name"] for player in game_state.players.values() if player["score"] != max_score
        ],
    }


if __name__ == "__main__":
    game_state.words = load_words()
    game_state.word = select_word(game_state.words)
    game_state.unrevealed_word = generate_unrevealed_word(game_state.word)

    socketio.run(app, debug=True)
