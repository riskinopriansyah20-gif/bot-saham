import telebot
import yfinance as yf
import threading
import time
import os
import pandas as pd

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

# ===============================
# LIST SAHAM (CONTOH)
# ===============================
tickers = [
    "BBRI.JK","BBCA.JK","TLKM.JK","BMRI.JK","ASII.JK",
    "AMRT.JK","BIPI.JK","PURA.JK","DEWA.JK"
]

# ===============================
# SAFE PRICE EXTRACTOR (ANTI ERROR)
# ===============================
def get_last_value(data, column_name):
    try:
        # Jika MultiIndex → ambil level pertama
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
# MARKET SCANNER
# ===============================
def scan_market():
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
            volume = get_last_value(data, "Volume")

            if open_price is None or close_price is None:
                continue

            if open_price == 0:
                continue

            price_change = (close_price - open_price) / open_price * 100

            if True:
                message = (
                    f"🔥 {ticker}\n"
                    f"Change: {round(price_change,2)}%\n"
                    f"Volume: {int(volume) if volume else 0}"
                )

                bot.send_message(CHAT_ID, message)

        except Exception as e:
            print("Error:", ticker, e)
            continue


# ===============================
# AUTO LOOP
# ===============================
def auto_scan():
    while True:
        try:
            scan_market()
            time.sleep(300)  # 5 menit
        except:
            time.sleep(10)


# ===============================
# TELEGRAM COMMAND
# ===============================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot Saham Intraday Aktif 🔥")


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    print("Bot Saham Running...")

    scan_thread = threading.Thread(target=auto_scan)
    scan_thread.daemon = True
    scan_thread.start()

    bot.infinity_polling(skip_pending=True)
