import os
import random
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, Response
from supabase import create_client

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "loading_experiment_secret")

SCREENS = ["blank", "stay", "spinner", "skeleton", "game"]
DATA_PASSWORD = os.environ.get("DATA_PASSWORD", "admin")


def get_db():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def next_screen():
    queue = session.get("screen_queue", [])
    if not queue:
        queue = SCREENS[:]
        random.shuffle(queue)
    screen = queue.pop()
    session["screen_queue"] = queue
    return screen


@app.route("/debug-env")
def debug_env():
    url = os.environ.get("SUPABASE_URL", "NOT SET")
    key = os.environ.get("SUPABASE_KEY", "NOT SET")
    return jsonify(url=url, key_length=len(key), key_prefix=key[:10] if key != "NOT SET" else "NOT SET")


@app.route("/")
def index():
    return render_template("start.html")


@app.route("/loading")
def loading():
    if "screen" not in session:
        session["user_id"] = session.get("user_id", str(uuid.uuid4()))
        session["screen"] = next_screen()
        session["start_time"] = datetime.now().isoformat()
    return render_template("loading.html", screen=session["screen"])


@app.route("/event", methods=["POST"])
def event():
    body = request.get_json()
    record = {
        "user_id": session.get("user_id"),
        "screen": session.get("screen"),
        "start_time": session.get("start_time"),
        "event": body.get("event"),
        "wait_seconds": body.get("wait_seconds"),
        "game_score": body.get("game_score"),
        "timestamp": datetime.now().isoformat(),
    }
    get_db().table("responses").insert(record).execute()
    return jsonify(ok=True)


@app.route("/data")
def data_view():
    auth = request.authorization
    if not auth or auth.password != DATA_PASSWORD:
        return Response("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="data"'})
    return jsonify(get_db().table("responses").select("*").execute().data)


if __name__ == "__main__":
    app.run(debug=False)
