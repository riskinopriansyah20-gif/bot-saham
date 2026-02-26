import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot Saham Aktif 🔥")

@bot.message_handler(commands=['signal'])
def signal(message):
    bot.reply_to(message, "Belum ada signal hari ini.")

bot.infinity_polling()
