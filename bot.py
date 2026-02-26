import os
import telebot
import yfinance as yf
import threading
import time

# ==============================
# CONFIG
# ==============================

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

# ==============================
# LOAD TICKERS
# ==============================

def load_tickers():
    with open("tickers.txt", "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

tickers = load_tickers()

# ==============================
# MARKET CHECK (TEST MODE: ALWAYS OPEN)
# ==============================

def market_open():
    return True   # 🔥 TEST MODE AKTIF (scan jalan terus)

# ==============================
# SCANNER ENGINE
# ==============================

def scan_market():
    print("Scanning market...")

    for ticker in tickers:
        try:
            data = yf.download(ticker, period="1d", interval="5m")

            if data.empty:
                continue

            required_columns = ['Open', 'Close', 'Volume']
            if not all(col in data.columns for col in required_columns):
                continue

            last = data.iloc[-1]

            open_price = float(last['Open'])
            close_price = float(last['Close'])
            volume = int(last['Volume'])

            if open_price == 0:
                continue

            price_change = (close_price - open_price) / open_price * 100

            # === FILTER SINYAL ===
            if price_change > 3:
                message = (
                    f"🔥 {ticker}\n"
                    f"Change: {round(price_change,2)}%\n"
                    f"Volume: {volume}"
                )
                bot.send_message(CHAT_ID, message)

        except Exception as e:
            print("Error:", ticker, e)
            continue

# ==============================
# AUTO SCAN LOOP
# ==============================

def auto_scan():
    while True:
        print("Scanning cycle...")
        scan_market()
        time.sleep(300)  # 5 menit

# ==============================
# TELEGRAM COMMAND
# ==============================

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot Saham Intraday Aktif 🔥")

# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    print("Bot Saham Running...")

    scan_thread = threading.Thread(target=auto_scan)
    scan_thread.start()

    bot.infinity_polling(skip_pending=True)
