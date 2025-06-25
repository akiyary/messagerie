import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
messages = []

USERS_FILE = "users.json"

# === UTILS ===
def charger_utilisateurs():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({
                "admin": {"password": "admin123", "role": "admin"}
            }, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def sauvegarder_utilisateurs(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# === ROUTES MESSAGES ===
@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    if not data or "from" not in data or "text" not in data:
        return {"error": "Invalid data"}, 400
    messages.append({"from": data["from"], "text": data["text"]})
    return {"status": "ok"}

@app.route("/messages", methods=["GET"])
def get_messages():
    return jsonify(messages)

# === ROUTES UTILISATEURS ===
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
    return jsonify({"success": True, "message": "Compte créé"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    users = charger_utilisateurs()

    if username in users and users[username]["password"] == password:
        return jsonify({
            "success": True,
            "role": users[username]["role"]
        })
    return jsonify({"success": False, "message": "Identifiants invalides"}), 401

# === MAIN ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
