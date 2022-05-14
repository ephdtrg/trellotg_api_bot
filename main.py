import os
from dotenv import load_dotenv
import telebot

load_dotenv()

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_API_TOKEN"), parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

if __name__ == '__main__':
    print('start bot')
    bot.infinity_polling()