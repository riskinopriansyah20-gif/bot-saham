import telebot
import yfinance as yf
import threading
import time
import os
import pandas as pd

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

CHAT_ID = None  # Akan diisi otomatis setelah /start

# ===============================
# LIST SAHAM
# ===============================
tickers = [
    "BBRI.JK","BBCA.JK","TLKM.JK","BMRI.JK","ASII.JK",
    "AMRT.JK","BIPI.JK","PURA.JK","DEWA.JK"
]

# ===============================
# SAFE PRICE FUNCTION
# ===============================
def get_last_value(data, column_name):
    try:
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if column_name not in data.columns:
            return None

        value = data[column_name].iloc[-1]

        if pd.isna(value):
            return None

        return float(value)
    except:
        return None


# ===============================
# SCANNER
# ===============================
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

            if open_price == 0:
                continue

            price_change = (close_price - open_price) / open_price * 100

            # TEST MODE MALAM INI (1%)
            if price_change > 1:
                message = (
                    f"🔥 {ticker}\n"
                    f"Change: {round(price_change,2)}%"
                )

                try:
                    bot.send_message(CHAT_ID, message)
                except Exception as e:
                    print("Telegram Error:", e)

        except Exception as e:
            print("Scan Error:", ticker, e)


# ===============================
# AUTO LOOP
# ===============================
def auto_scan():
    while True:
        try:
            scan_market()
            time.sleep(300)
        except:
            time.sleep(10)


# ===============================
# START COMMAND
# ===============================
@bot.message_handler(commands=['start'])
def start(message):
    global CHAT_ID

    CHAT_ID = message.chat.id

    bot.reply_to(
        message,
        f"Bot Saham Aktif 🔥\nChat ID: {CHAT_ID}\nTest message berhasil."
    )

    print("CHAT_ID SET:", CHAT_ID)


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    print("Bot Saham Running...")

    bot.delete_webhook()
    time.sleep(1)

    scan_thread = threading.Thread(target=auto_scan)
    scan_thread.daemon = True
    scan_thread.start()

    while True:
        try:
            bot.polling(none_stop=True, interval=3, timeout=20)
        except Exception as e:
            print("Polling error:", e)
            time.sleep(5)
