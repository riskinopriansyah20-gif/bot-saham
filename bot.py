import telebot
import yfinance as yf
import pandas as pd
import threading
import time
import os
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(name)

CHAT_ID = None

# ======================
# LIST SAHAM
# ======================
tickers = [
    "BBRI.JK","BBCA.JK","TLKM.JK","BMRI.JK","ASII.JK",
    "AMRT.JK","BIPI.JK","PURA.JK","DEWA.JK"
]

# ======================
# SAFE VALUE
# ======================
def get_last_value(data, column_name):
    try:
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        value = data[column_name].iloc[-1]

        if pd.isna(value):
            return None

        return float(value)
    except:
        return None

# ======================
# SCAN MARKET
# ======================
def scan_market():
    global CHAT_ID

    if CHAT_ID is None:
        return

    print("Scanning market...")

    for ticker in tickers:
        try:
            data = yf.download(
                ticker,
                period="1d",
                interval="5m",
                progress=False
            )

            if data.empty:
                continue

            open_price = get_last_value(data, "Open")
            close_price = get_last_value(data, "Close")

            if open_price is None or close_price is None:
                continue

            change = (close_price - open_price) / open_price * 100

            if change > 1:
                bot.send_message(
                    CHAT_ID,
                    f"🔥 {ticker}\nChange: {round(change,2)}%"
                )

        except Exception as e:
            print("Scan error:", ticker, e)

# ======================
# AUTO LOOP
# ======================
def auto_scan():
    while True:
        try:
            scan_market()
            time.sleep(300)
        except:
            time.sleep(10)

# ======================
# TELEGRAM HANDLER
# ======================
@bot.message_handler(commands=['start'])
def start(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.reply_to(message, f"Bot Aktif 🔥\nChat ID: {CHAT_ID}")

# ======================
# WEBHOOK ROUTE
# ======================
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# ======================
# MAIN
# ======================
if __name__ == "__main__":
    print("Bot running in WEBHOOK mode...")

    bot.remove_webhook()
    time.sleep(1)

    RAILWAY_URL = os.getenv("RAILWAY_STATIC_URL")

    bot.set_webhook(url=f"https://{RAILWAY_URL}/{TOKEN}")

    scan_thread = threading.Thread(target=auto_scan)
    scan_thread.daemon = True
    scan_thread.start()

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
