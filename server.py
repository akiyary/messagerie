import os
from flask import Flask, request, jsonify

app = Flask(__name__)
messages = []

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # obligatoire pour Render
    app.run(host="0.0.0.0", port=port)

