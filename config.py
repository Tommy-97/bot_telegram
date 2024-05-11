# config.py
from aiogram import Bot, types


async def send_message_to_user(chat_id, text):
    bot = Bot(token='KEY')
    await bot.send_message(chat_id, text)


API_TOKEN = 'KEY'

SQLALCHEMY_URL = "sqlite:///F:/SQLete/Auto_base.db"
