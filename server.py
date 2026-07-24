from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
CORS(app)

MESSAGES_FILE = "messages.json"
USERS_FILE = "users.json"
DELAI_EN_LIGNE = timedelta(seconds=15)   # affiché "en ligne" si heartbeat récent
EXPIRATION = timedelta(seconds=25)       # supprimé si aucun heartbeat depuis ce délai


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


def charger_users():
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            contenu = f.read().strip()
            if not contenu:
                return {}
            return json.loads(contenu)
    except json.JSONDecodeError as e:
        print(f"[ERREUR JSON] users.json mal formé : {e}")
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    except Exception as e:
        print(f"[ERREUR] Lecture users.json impossible : {e}")
        return {}


def sauvegarder_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERREUR] Écriture users.json impossible : {e}")


def nettoyer_users(users):
    """Retire les pseudos dont le heartbeat est trop vieux (page fermée
    sans prévenir le serveur, crash du navigateur, etc.)."""
    maintenant = datetime.utcnow()
    valides = {}
    for pseudo, horodatage in users.items():
        try:
            vu = datetime.fromisoformat(horodatage)
            if (maintenant - vu) < EXPIRATION:
                valides[pseudo] = horodatage
        except Exception:
            continue
    return valides


def marquer_actif(pseudo):
    """Enregistre/rafraîchit l'horodatage du dernier signe de vie d'un pseudo."""
    if not pseudo:
        return
    users = nettoyer_users(charger_users())
    users[pseudo] = datetime.utcnow().isoformat()
    sauvegarder_users(users)


def retirer_utilisateur(pseudo):
    """Supprime explicitement un pseudo (fermeture / rechargement de page)."""
    if not pseudo:
        return
    users = nettoyer_users(charger_users())
    users.pop(pseudo, None)
    sauvegarder_users(users)


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

    marquer_actif(data["from"])

    return jsonify({"success": True, "message": "Message envoyé"}), 201


@app.route("/connect", methods=["POST"])
def connect_user():
    """Enregistre/rafraîchit un pseudo comme connecté (appelé au chargement
    de la page et périodiquement en heartbeat par le client)."""
    data = request.get_json(silent=True) or {}
    pseudo = (data.get("from") or "").strip()
    if not pseudo:
        return jsonify({"success": False, "message": "Pseudo manquant"}), 400
    marquer_actif(pseudo)
    return jsonify({"success": True}), 200


@app.route("/disconnect", methods=["POST"])
def disconnect_user():
    """Retire un pseudo (fermeture ou rechargement de la page côté client,
    appelé via sendBeacon)."""
    data = request.get_json(silent=True) or {}
    pseudo = (data.get("from") or "").strip()
    retirer_utilisateur(pseudo)
    return jsonify({"success": True}), 200


@app.route("/users", methods=["GET"])
def get_users():
    users = nettoyer_users(charger_users())
    maintenant = datetime.utcnow()
    liste = []
    for pseudo, horodatage in users.items():
        try:
            vu = datetime.fromisoformat(horodatage)
            en_ligne = (maintenant - vu) < DELAI_EN_LIGNE
        except Exception:
            en_ligne = False
        liste.append({"name": pseudo, "online": en_ligne})
    return jsonify(liste)


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
def sauvegarder_messages(messages):
    try:
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERREUR] Écriture impossible : {e}")


def charger_users():
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            contenu = f.read().strip()
            if not contenu:
                return {}
            return json.loads(contenu)
    except json.JSONDecodeError as e:
        print(f"[ERREUR JSON] users.json mal formé : {e}")
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    except Exception as e:
        print(f"[ERREUR] Lecture users.json impossible : {e}")
        return {}


def sauvegarder_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERREUR] Écriture users.json impossible : {e}")


def marquer_actif(pseudo):
    """Enregistre l'horodatage du dernier message d'un pseudo."""
    if not pseudo:
        return
    users = charger_users()
    users[pseudo] = datetime.utcnow().isoformat()
    sauvegarder_users(users)


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

    marquer_actif(data["from"])

    return jsonify({"success": True, "message": "Message envoyé"}), 201


@app.route("/users", methods=["GET"])
def get_users():
    users = charger_users()
    maintenant = datetime.utcnow()
    liste = []
    for pseudo, horodatage in users.items():
        try:
            vu = datetime.fromisoformat(horodatage)
            en_ligne = (maintenant - vu) < DELAI_EN_LIGNE
        except Exception:
            en_ligne = False
        liste.append({"name": pseudo, "online": en_ligne})
    return jsonify(liste)


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
