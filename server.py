from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

# --- stockage en mémoire (à remplacer par ta vraie logique / DB si besoin) ---
messages = []  # liste de { from, text, media?, timestamp }
utilisateurs_vus = {}  # pseudo -> dernier moment vu actif

DELAI_EN_LIGNE = timedelta(seconds=30)  # inactif après 30s sans activité
TAILLE_MAX_MEDIA = 5 * 1024 * 1024  # 5 Mo, doit matcher la limite côté client


def marquer_actif(pseudo):
    """Appelée à chaque envoi de message pour compter le pseudo comme utilisateur actif."""
    if pseudo:
        utilisateurs_vus[pseudo] = datetime.utcnow()


def taille_base64(data_url):
    """Estime la taille en octets d'une data URL base64 (ex: 'data:image/png;base64,AAAA...')."""
    try:
        b64 = data_url.split(",", 1)[1]
    except (IndexError, AttributeError):
        return 0
    return int(len(b64) * 3 / 4)


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"ok": True})


@app.route("/users", methods=["GET"])
def get_users():
    maintenant = datetime.utcnow()
    liste = [
        {
            "name": pseudo,
            "online": (maintenant - vu) < DELAI_EN_LIGNE
        }
        for pseudo, vu in utilisateurs_vus.items()
    ]
    return jsonify(liste)


@app.route("/messages", methods=["GET"])
def get_messages():
    return jsonify(messages)


@app.route("/send", methods=["POST"])
def send():
    data = request.get_json(force=True, silent=True) or {}
    pseudo = (data.get("from") or "").strip()
    texte = (data.get("text") or "").strip()
    media = data.get("media")  # { name, type, size, dataUrl } ou None

    if not pseudo:
        return jsonify({"success": False, "message": "signature manquante"}), 400
    if not texte and not media:
        return jsonify({"success": False, "message": "message vide"}), 400

    message = {
        "from": pseudo,
        "text": texte,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if media:
        data_url = media.get("dataUrl", "")
        nom = media.get("name", "fichier")
        media_type = media.get("type", "application/octet-stream")
        taille_annoncee = media.get("size", 0)

        if not data_url.startswith("data:"):
            return jsonify({"success": False, "message": "média invalide"}), 400

        taille_reelle = taille_base64(data_url)
        if taille_reelle > TAILLE_MAX_MEDIA:
            return jsonify({
                "success": False,
                "message": f"média trop volumineux ({taille_reelle} octets, max {TAILLE_MAX_MEDIA})"
            }), 413

        message["media"] = {
            "name": nom,
            "type": media_type,
            "size": taille_annoncee or taille_reelle,
            "dataUrl": data_url,
        }

    marquer_actif(pseudo)
    messages.append(message)

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)    pseudo = data.get("from")
    texte = data.get("text")

    marquer_actif(pseudo)  # <-- ligne à ajouter dans ta route /send actuelle

    # ... ta logique existante pour stocker/renvoyer le message ...
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
