import os
import telebot
import yfinance as yf
import time
import threading
import datetime

def market_open():
    now = datetime.datetime.now()
    return now.hour >= 9 and now.hour <= 16

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

# Load ticker list
def load_tickers():
    with open("tickers.txt", "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

tickers = load_tickers()

def scan_market():
    print("Scanning market...")
    for ticker in tickers:
        try:
            data = yf.download(ticker, period="1d", interval="5m", progress=False)

            if len(data) < 2:
                continue

            last = data.iloc[-1]
            prev = data.iloc[-2]

            price_change = (last["Close"] - prev["Close"]) / prev["Close"] * 100
            volume_spike = last["Volume"] > prev["Volume"] * 1.5

            if price_change > 1 and volume_spike:
                message = (
                    f"🚀 {ticker}\n"
                    f"Price: {round(last['Close'],2)}\n"
                    f"Change: +{round(price_change,2)}%\n"
                    f"Volume Spike!"
                )
                bot.send_message(CHAT_ID, message)

        except Exception as e:
            print("Error:", ticker, e)

def auto_scan():
    while True:

        if not market_open():
            print("Market closed...")
            time.sleep(300)
            continue

        print("Scanning cycle...")
        scan_market()

        time.sleep(300)  # 5 menit delay

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot Saham Intraday Aktif 🔥")


if __name__ == "__main__":
    print("Bot Saham Running...")

    # Jalankan scanner di background thread
    scan_thread = threading.Thread(target=auto_scan)
    scan_thread.start()

    # Telegram listener tetap aktif
    bot.infinity_polling(skip_pending=True)
