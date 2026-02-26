import os
from flask import Flask, request
import telebot

# ==============================
# CONFIG
# ==============================

TOKEN = os.environ.get("BOT_TOKEN")  # simpan token di Railway Variables
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# ==============================
# TELEGRAM COMMANDS
# ==============================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Bot Saham Aktif 🔥\nChat ID: {chat_id}\nServer Webhook Running ✅")

# ==============================
# WEBHOOK ENDPOINT
# ==============================

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Invalid request', 403

# ==============================
# ROOT TEST
# ==============================

@app.route('/')
def index():
    return "Bot Saham Webhook Active 🚀", 200

# ==============================
# MAIN (LOCAL TEST ONLY)
# ==============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
