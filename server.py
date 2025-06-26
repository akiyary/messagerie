from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

MESSAGES_FILE = "messages.json"

def charger_messages():
    if not os.path.exists(MESSAGES_FILE) or os.path.getsize(MESSAGES_FILE) == 0:
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

    try:
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            contenu = f.read().strip()
            if not contenu:
                return []
            return json.loads(contenu)
    except json.JSONDecodeError as e:
        print(f"[ERREUR JSON] Fichier mal formé : {e}")
        # Réinitialise le fichier corrompu
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    except Exception as e:
        print(f"[ERREUR] Lecture impossible : {e}")
        return []

def sauvegarder_messages(messages):
    try:
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERREUR] Écriture impossible : {e}")

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

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong"}), 200

# === ROUTE TEMPORAIRE POUR RÉINITIALISER messages.json ===
@app.route("/reset", methods=["GET"])
def reset_messages():
    try:
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return jsonify({"success": True, "message": "messages.json réinitialisé"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)



