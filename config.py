#config.py
from aiogram import Bot, types


async def send_message_to_user(chat_id, text):
    bot = Bot(token="6969199222:AAFCiKI3cZbVnrhDhsyYZDpW3LBzFW36Eiw")  
    await bot.send_message(chat_id, text)



API_TOKEN = '6969199222:AAFCiKI3cZbVnrhDhsyYZDpW3LBzFW36Eiw'

SQLALCHEMY_URL = "sqlite:///F:/SQLete/Auto_base.db"

