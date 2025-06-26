from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

USERS_FILE = "users.json"
MESSAGES_FILE = "messages.json"

def charger_utilisateurs():
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        users = {"admin": {"password": "admin123", "role": "admin"}}
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        return users

    try:
        with open(USERS_FILE, "r") as f:
            contenu = f.read().strip()
            if not contenu:
                raise json.JSONDecodeError("Empty file", "", 0)
            return json.loads(contenu)
    except (json.JSONDecodeError, ValueError):
        users = {"admin": {"password": "admin123", "role": "admin"}}
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        return users

def sauvegarder_utilisateurs(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def charger_messages():
    if not os.path.exists(MESSAGES_FILE) or os.path.getsize(MESSAGES_FILE) == 0:
        with open(MESSAGES_FILE, "w") as f:
            json.dump([], f, indent=2)
        return []
    try:
        with open(MESSAGES_FILE, "r") as f:
            contenu = f.read().strip()
            if not contenu:
                raise json.JSONDecodeError("Empty file", "", 0)
            return json.loads(contenu)
    except (json.JSONDecodeError, ValueError):
        with open(MESSAGES_FILE, "w") as f:
            json.dump([], f, indent=2)
        return []

def sauvegarder_messages(messages):
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)

# Charger les messages au démarrage
messages = charger_messages()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Champs manquants"}), 400

    users = charger_utilisateurs()

    if username in users:
        return jsonify({"success": False, "message": "Utilisateur existe déjà"}), 409

    users[username] = {"password": password, "role": "user"}
    sauvegarder_utilisateurs(users)

    return jsonify({"success": True, "message": "Inscription réussie"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Champs manquants"}), 400

    users = charger_utilisateurs()

    if username not in users or users[username]["password"] != password:
        return jsonify({"success": False, "message": "Identifiants incorrects"}), 401

    return jsonify({"success": True, "role": users[username].get("role", "user")})

@app.route("/messages", methods=["GET"])
def get_messages():
    global messages
    return jsonify(messages)

@app.route("/send", methods=["POST"])
def send_message():
    global messages
    data = request.get_json()
    sender = data.get("from")
    text = data.get("text")

    if not sender or not text:
        return jsonify({"success": False, "message": "Champs manquants"}), 400

    message = {"from": sender, "text": text}
    messages.append(message)
    sauvegarder_messages(messages)

    return jsonify({"success": True, "message": "Message envoyé"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
