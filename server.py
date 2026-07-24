from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

# --- stockage en mémoire (à remplacer par ta vraie logique / DB si besoin) ---
# clé = pseudo, valeur = dernier moment où on a vu ce pseudo actif
utilisateurs_vus = {}

DELAI_EN_LIGNE = timedelta(seconds=30)  # inactif après 30s sans activité


def marquer_actif(pseudo):
    """Appelle cette fonction chaque fois qu'un pseudo envoie un message
    (par ex. dans ta route /send existante), pour le compter comme utilisateur."""
    if pseudo:
        utilisateurs_vus[pseudo] = datetime.utcnow()


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


# --- exemple d'intégration dans ta route /send existante ---
@app.route("/send", methods=["POST"])
def send():
    data = request.get_json(force=True)
    pseudo = data.get("from")
    texte = data.get("text")

    marquer_actif(pseudo)  # <-- ligne à ajouter dans ta route /send actuelle

    # ... ta logique existante pour stocker/renvoyer le message ...
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
