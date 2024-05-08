#common.py
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

from config import API_TOKEN

#from database import get_product_price
#from db_utils import get_user_by_email, save_product

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def notify_user(user_id: int, message_text: str):
    try:
        await bot.send_message(user_id, message_text)
    except Exception as e:
        print(f"An error occurred while sending notification to user {user_id}: {e}")
