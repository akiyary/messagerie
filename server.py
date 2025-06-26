from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

USERS_FILE = "users.json"

# Fonction pour charger les utilisateurs
def charger_utilisateurs():
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        # Créer un fichier avec un compte admin par défaut
        users = {
            "admin": {"password": "admin123", "role": "admin"}
        }
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        return users

    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Fichier JSON corrompu. Réinitialisation...")
        users = {
            "admin": {"password": "admin123", "role": "admin"}
        }
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        return users

# Fonction pour sauvegarder les utilisateurs
def sauvegarder_utilisateurs(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# Route pour l'inscription
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

# Lancer le serveur
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

