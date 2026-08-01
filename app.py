import json
import os
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = "loading_experiment_secret"

DATA_FILE = "data.json"
SCREENS = ["blank", "stay", "spinner", "skeleton", "game"]


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def index():
    return render_template("start.html")


@app.route("/loading")
def loading():
    screen = random.choice(SCREENS)
    session["screen"] = screen
    session["start_time"] = datetime.now().isoformat()
    return render_template("loading.html", screen=screen)


@app.route("/event", methods=["POST"])
def event():
    body = request.get_json()
    record = {
        "screen": session.get("screen"),
        "start_time": session.get("start_time"),
        "event": body.get("event"),          # "close" | "refresh" | "waited"
        "wait_seconds": body.get("wait_seconds"),
        "game_score": body.get("game_score"),
        "timestamp": datetime.now().isoformat(),
    }
    data = load_data()
    data.append(record)
    save_data(data)
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(debug=True)
