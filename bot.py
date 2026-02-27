import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.getenv("TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Bot Saham Webhook Active 🚀", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "Bot Saham Aktif 🔥\nServer Webhook Running ✅"
                }
            )

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
