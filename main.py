import os
from dotenv import load_dotenv
import requests
import json
import telebot
import logging

from redis_client import RedisClient

load_dotenv()

LOGGING_FORMAT = '%(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_API_TOKEN"), parse_mode=None)
bot.add_custom_filter(telebot.custom_filters.ChatFilter())

BOT_CHAT_ID =  os.getenv("TELEGRAM_BOT_CHAT_ID")
logging.info(BOT_CHAT_ID)

def send_to_trello_api(title, description) -> dict:
    query = {
       'idList':  os.getenv("TRELLO_LIST_ID"),
       'key': os.getenv("TRELLO_API_KEY"),
       'token': os.getenv("TRELLO_API_TOKEN"),
        "name": title,
        "desc": description
    }

    response = requests.request(
        "POST",
        "https://api.trello.com/1/cards",
        headers={"Accept": "application/json"},
        params=query
    )

    return response.json()

def redis_save_or_update(message: telebot.types.Message):
    redis_client = RedisClient()
    db_msg = redis_client.connection.get(message.chat.id)
    logging.info(f"REDIS GET: {message.chat.id} has message in db: {db_msg}")

    redis_client.connection.set(message.id, message.text)
    logging.info(f"REDIS SET: {message.id} saved message {message.text}")

def redis_get_and_delete(message):
    redis_client = RedisClient()
    db_keys = redis_client.connection.keys()
    key_values = []
    for key in db_keys:
        key_values.append(redis_client.connection.getdel(key).decode('utf-8'))

    message_to_send = '\n\n'.join(key_values)
    return message_to_send


@bot.message_handler(chat_id=[int(BOT_CHAT_ID)], commands=['add'])
def add_to_trello(message: telebot.types.Message):
    saved_msg = redis_get_and_delete(message)
    if not saved_msg:
        bot.reply_to(message, "No pending messages in db")
        return

    trello_title = message.text.split(' ', maxsplit=1)[1]
    trello_response = send_to_trello_api(trello_title, saved_msg)
    bot.reply_to(message, f"Messages sent to Trello \n {trello_response.get('url')}")

@bot.message_handler(chat_id=[int(BOT_CHAT_ID)], func=lambda message: True)
def add_as_card(message: telebot.types.Message):
    redis_save_or_update(message)

@bot.message_handler(commands=['get_chat_id'])
def get_chat_id(message: telebot.types.Message):
    bot.reply_to(message, f"{str(message.chat.id)} {BOT_CHAT_ID}")

if __name__ == '__main__':
    print('start bot')
    bot.infinity_polling()