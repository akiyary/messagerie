from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

MESSAGES_FILE = "messages.json"

def charger_messages():
    if not os.path.exists(MESSAGES_FILE) or os.path.getsize(MESSAGES_FILE) == 0:
        with open(MESSAGES_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(MESSAGES_FILE, "r") as f:
            contenu = f.read().strip()
            if not contenu:
                return []
            return json.loads(contenu)
    except json.JSONDecodeError:
        return []

def sauvegarder_messages(messages):
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)

@app.route("/messages", methods=["GET"])
def get_messages():
    messages = charger_messages()
    return jsonify(messages)

@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    if not data or "from" not in data or "text" not in data:
        return jsonify({"success": False, "message": "Champs manquants"}), 400
    
    messages = charger_messages()
    messages.append({"from": data["from"], "text": data["text"]})
    sauvegarder_messages(messages)
    return jsonify({"success": True, "message": "Message envoyé"}), 201

# === KEEP-ALIVE ===
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

