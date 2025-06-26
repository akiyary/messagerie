from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

USERS_FILE = "users.json"

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


