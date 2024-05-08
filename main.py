# main.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import Message

from common import dp
from config import API_TOKEN
from database import (get_message_from_database,
                      some_function_where_you_call_fetch_information)
# from database import get_user_info_by_email, save_product
from handlers import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# add_new_user_with_async_session,
# async_session, create_tables, get_user_by_email,
async def main_logic(bot: Bot, dp: Dispatcher):
    # Установка middleware для логирования
    dp.middleware.setup(LoggingMiddleware())

    # Регистрация обработчиков сообщений
    dp.register_message_handler(help_command, commands=['help'])
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(
        get_user_info_command, commands=['get_user_info'])
    dp.register_message_handler(fetch_db_info_command, commands=[
                                'fetch_db_info'])  # Исправлено здесь
    dp.register_message_handler(
        process_get_product_info_message, commands=['get_product'])
    dp.register_message_handler(some_function_where_you_call_fetch_information, commands=[
                                'some_command'])  # Вот здесь

    # Регистрация обработчиков callback-запросов
    dp.register_callback_query_handler(
        process_get_info_from_db, text_contains="get_info_from_db")
    dp.register_callback_query_handler(process_cancel, text_contains="cancel")
    dp.register_callback_query_handler(
        process_stop_notifications, text_contains="stop_notifications")
    dp.register_callback_query_handler(
        process_get_product_info_callback, text_contains="get_product_info")

    # Запуск бесконечного цикла получения обновлений
    await dp.start_polling()


async def main():
    try:
        # Create database tables if they don't exist
        await create_tables()

        # Connect to the database session
        async with Bot(token=API_TOKEN) as bot:
            dp = Dispatcher(bot)
            await add_new_user("Tomms", "hhkjkjk5kkkui110@gmail.com")
            user = await get_user_by_email("hhkjkjk5kkkui110@gmail.com")
            if user:
                print("User found:", user)
            else:
                print("User with email 'hhkjkjk5kkkui110@gmail.com' not found.")

            # Start the main logic of your application
            await main_logic(bot, dp)

            # Keep the script running
            while True:
                await asyncio.sleep(10)

    except Exception as e:
        print(f"An error occurred: {e}")


async def add_new_user_if_not_exists(email: str):
    try:
        # Проверка существования пользователя с указанным email
        existing_user = await get_user_by_email(email)
        if existing_user:
            print(f"User with email '{email}' already exists.")
        else:
            # Создание нового пользователя с указанным email
            await add_new_user(name="Tomms", email=email)
            print(f"New user with email '{email}' added successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


async def process_get_product_info_message(message):
    text = message.text
    article = text.split()[-1]
    price = '20000руб'
    async with async_session() as session:
        product_info = await get_product_info(article, session, save_product, message, bot, message.from_user.id, price=price)
        if product_info:
            print("Product info:", product_info)
        else:
            print("Product not found.")


async def process_get_product_info_callback(callback_query):
    try:
        text = callback_query.data
        article = text.split()[-1]
        async with async_session() as session:
            product_info = await get_product_info(article, session, save_product, callback_query.message, bot, callback_query.from_user.id)
            if product_info:
                print("Product info:", product_info)
            else:
                print("Product not found.")
    except AttributeError as e:
        # Properly log the error instead of just printing
        logger.error(
            "CallbackQuery object has no attribute 'text'", exc_info=e)


async def get_user_info_command(message):
    email = message.text.split()[-1]  # Extracting email from the message text
    async with async_session() as session:
        # Pass the email argument
        user = await get_user_info_by_email(session, email)
        if user:
            print("User info:", user)
        else:
            print("User not found.")


if __name__ == '__main__':
    try:
        # Create database tables if they don't exist
        asyncio.run(create_tables())

        # Connect to the bot and start the main logic
        bot = Bot(token=API_TOKEN)
        dispatcher = Dispatcher(bot)
        asyncio.run(main_logic(bot, dispatcher))

    except Exception as e:
        print(f"An error occurred: {e}")
