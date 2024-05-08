# handlers.py
import asyncio
from asyncio.log import logger
import dbm
import select
from ast import Return
from curses import wrapper
from datetime import datetime
from functools import wraps
from typing import Union

from aiogram import bot, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.utils.markdown import hcode

from base import send_notification
from common import dp
from config import API_TOKEN
from database import (add_new_user, async_session, create_tables,
                      get_product_info, get_product_price, get_user_by_email,
                      get_user_info_by_email, get_users_from_database, save_product
                      )
from main import bot, dp, main_logic  # session
from models import User
from run_bot import save_product


class YourState(StatesGroup):
    SomeState = State()


# class States(StatesGroup):
 #   get_user_info = State()


def get_session_for_user(func):
    @wraps(func)
    async def wrapper(message: types.Message, state: FSMContext, *args, **kwargs):
        async with async_session() as session:
            return await func(message, state, session, *args, **kwargs)
    return wrapper


@dp.message_handler(commands=['get_user_info'])
async def get_user_info_command(message: types.Message):
    email = "tommy155u000i110@gmail.com"
    async with async_session() as session:
        user_info = await get_user_info_by_email(session, email)

        if user_info:
            response_text = f"Информация о пользователе:\n{user_info}"
        else:
            response_text = "Пользователь не найден."

        await message.answer(response_text)


@dp.message_handler(state=YourState.SomeState)
@get_session_for_user
async def process_article(message: types.Message, state: FSMContext, session):
    article = message.text
    product_info = await get_product_info(article, session)
    if product_info:
        await message.answer(product_info)
    else:
        await message.answer("Товар не найден.")
    await state.finish()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(
            text="Получить информацию по товару", callback_data="get_product_info"),
        types.InlineKeyboardButton(
            text="Остановить уведомления", callback_data="stop_notifications"),
        types.InlineKeyboardButton(
            text="Получить информацию из БД", callback_data="fetch_information_from_db")  # get_info_from_db
    )
    await dp.bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard_markup)


@dp.callback_query_handler(text_contains="stop_notifications")
async def process_stop_notifications(callback_query: types.CallbackQuery):
    await callback_query.answer()

    await stop_notifications_function()


async def stop_notifications_function():
    pass


@dp.callback_query_handler(text_contains="fetch_information_from_db")
async def process_fetch_information_from_db(callback_query: types.CallbackQuery):
    await callback_query.answer()
    db_info = await fetch_information_from_db()
    if db_info:
        response_text = "Информация из базы данных:\n"
        for info in db_info:
            response_text += f"{info}\n"
    else:
        response_text = "Информация из базы данных отсутствует."
    await callback_query.message.answer(response_text)


@dp.message_handler(Command("fetch_db_info"))
async def fetch_information_from_db():
    try:
        async with async_session() as session:
            query_result = await session.execute(select(User))
            information = query_result.scalars().all()
            return information  # Возвращаем результаты запроса
    except Exception as e:
        print(
            f"An error occurred while fetching information from the database: {e}")
        return None


# Глобальные переменные для session и save_product
global_session = None
global_save_product = None

# Обработчик команды "get_product"


@dp.message_handler(Command("get_product"))
async def get_product_info_command(message: types.Message):
    global global_session
    global global_save_product

    article = message.text.split()[-1]
    if global_session is None:
        global_session = async_session()
    if global_save_product is None:
        global_save_product = save_product

    async with global_session as session:
        product_info = await get_product_info(article, session, global_save_product)

        if product_info:
            # If product info is found, send it to the user
            response = f"Name: {product_info['name']}\n"
            response += f"Price: {product_info['price']}\n"
            response += f"Rating: {product_info['rating']}\n"
            response += f"Quantity: {product_info['quantity']}\n"
            response += f"Article: {product_info['article']}"
            await message.answer(response)
        else:
            # If product info is not found, inform the user
            await message.answer("Product not found.")


# Обработчик колбэка "get_product_info"
@dp.callback_query_handler(text_contains="get_product_info")
async def process_get_product_info(callback_query: types.CallbackQuery):
    global global_session
    global global_save_product

    await callback_query.answer()
    article = "123456"  # Замените на фактический номер статьи, полученный от пользователя

    if global_session is None:
        global_session = async_session()
    if global_save_product is None:
        global_save_product = save_product

    # Пытаемся получить информацию о продукте
    async with global_session as session:
        product_info = await get_product_info(article, session, global_save_product, callback_query.message, bot, callback_query.from_user.id)
        if product_info:
            response_text = (
                f"Информация о продукте с артикулом {hcode(article)}:\n"
                f"Название: {product_info['name']}\n"
                f"Цена: {product_info['price']}\n"
                f"Рейтинг: {product_info['rating']}\n"
                f"Количество: {product_info['quantity']}"
            )
        else:
            response_text = "Продукт с указанным артикулом не найден."

        # Отправляем ответ пользователю
        await callback_query.message.answer(response_text)


@dp.message_handler(state=YourState.SomeState)
async def process_article(message: types.Message, state: FSMContext):
    article = message.text
    user_id = message.from_user.id
    async for session in get_session_for_user(user_id):
        product_info = await get_product_info(article, session)
        await message.answer(product_info)
    await state.finish()


# Обработчик состояния, в котором ожидается ввод артикула товара
@dp.message_handler(state=YourState.SomeState)
async def process_product_article(message: types.Message, state: FSMContext):
    product_article = message.text  # Получаем введенный пользователем артикул товара
    # Запрашиваем информацию о товаре по артикулу
    product_info = await get_product_info(product_article)
    if product_info:
        await message.answer(product_info)
    else:
        await message.answer("Товар не найден.")

    await state.finish()  # Завершаем состояние после обработки запроса


@dp.message_handler(commands=['notify_users'])
async def notify_users_command(message: types.Message):
    async with async_session() as session:
        print("Searching for users...")
        users = await get_users_from_database(session)
        for user in users:
            await send_notification(user)
    await message.answer("Уведомления отправлены.")


@dp.callback_query_handler(text_contains="stop_notifications")
async def process_stop_notifications(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await stop_notifications_function()
    await callback_query.message.answer("Уведомления остановлены.")


@dp.message_handler(commands=['get_info_from_db'])
async def get_info_from_db_command(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        types.InlineKeyboardButton(
            text="Подтвердить", callback_data="confirm"),
        types.InlineKeyboardButton(text="Отмена", callback_data="cancel")
    )
    await message.answer("Вы уверены, что хотите получить информацию из базы данных?",
                         reply_markup=keyboard_markup)
    await YourState.GetInfoConfirmation.set()


@dp.callback_query_handler(text_contains="get_info_from_db")
async def process_get_info_from_db(callback_query: types.CallbackQuery):
    await callback_query.answer()
    email = callback_query.from_user.email
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    response_text = f"Информация для пользователя {callback_query.from_user.first_name}:\n\n" \
                    f"Адрес электронной почты: {email}\n" \
                    f"Текущее время: {current_time}\n" \
                    f"Сегодняшняя дата: {current_date}"
    await callback_query.message.answer(response_text)


@dp.callback_query_handler(text_contains="get_info_from_db")
async def process_get_info_from_db(callback_query: types.CallbackQuery):
    try:
        await callback_query.answer()
        email = callback_query.from_user.email
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        response_text = f"Информация для пользователя {callback_query.from_user.first_name}:\n\n" \
                        f"Адрес электронной почты: {email}\n" \
                        f"Текущее время: {current_time}\n" \
                        f"Сегодняшняя дата: {current_date}"
        await callback_query.message.answer(response_text)

        # Call the save_product function here with the necessary arguments
        # await save_product(session, name, article, price, rating, quantity)

    except Exception as e:
        logger.error(f"An error occurred in process_get_info_from_db: {e}")


@dp.callback_query_handler(text_contains="cancel")
async def process_cancel(callback_query: types.CallbackQuery):
    await callback_query.answer("Действие отменено.")


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    response_text = "Это помощь. Здесь вы можете указать, как пользоваться вашим ботом."
    await message.answer(response_text)


@dp.message_handler(commands=['get_user_info'])
async def get_user_info_command(message: types.Message):
    try:
        # Extract the email from the message text
        email = message.text.split()[-1]
        user_info = await get_user_info_by_email(email)
        if user_info:
            # Process the user information
            await message.answer(f"User info: {user_info}")
        else:
            await message.answer("User not found.")
    except Exception as e:
        # Handle any exceptions that might occur during the operation
        logger.error(f"An error occurred while fetching user info: {e}")
        await message.answer("An error occurred while fetching user info.")


# Обработчик для запроса информации из базы данных
@dp.message_handler(commands=['fetch_db_info'])
async def fetch_db_info_command(message: types.Message, state: FSMContext):
    try:
        async with async_session() as session:
            information = await fetch_information_from_db(session)

            if information:
                info_text = "Информация из базы данных:\n"
                for info in information:
                    info_text += f"ID: {info.id}, Name: {info.name}, Email: {info.email}, Created At: {info.created_at}\n"
                # Changed from message_or_callback to message
                await message.answer(info_text)
            else:
                await message.answer("Информация из базы данных не найдена.")
    except Exception as e:
        await message.answer(f"An error occurred: {e}")


# Handler for the command '/get_users'
@dp.message_handler(commands=['get_users'])
async def get_users_command(message: types.Message):
    try:
        async with async_session() as session:
            # Fetch user information from the database
            users = await get_users_from_database(session)

            if users:
                # Prepare the response text
                response_text = "Список пользователей:\n"
                for user in users:
                    response_text += f"Имя: {user.name}, Email: {user.email}\n"

                # Send the response message
                await message.answer(response_text)
            else:
                await message.answer("В базе данных нет пользователей.")
    except Exception as e:
        await message.answer(f"An error occurred: {e}")


# Обработчик нажатия кнопки и команды для запроса информации из базы данных
@dp.callback_query_handler(text_contains="fetch_information_from_db")
@dp.message_handler(commands=['fetch_db_info'])
async def fetch_db_info_callback(message_or_callback: Union[types.Message, CallbackQuery], state: FSMContext):
    # Changed from fetch_db_info_handler to fetch_db_info_command
    await fetch_db_info_command(message_or_callback, state)


async def fetch_information_from_db(session):
    try:
        query_result = await session.execute(select(User))
        information = query_result.scalars().all()
        print("Information fetched successfully")
        return information
    except Exception as e:
        print(
            f"An error occurred while fetching information from the database: {e}")
        return None


# Реализация команды для получения списка пользователей из базы данных
# @dp.message_handler(commands=['get_users'])
# async def get_users_command(message: types.Message):
 #   async with async_session() as session:  # Создаем сессию базы данных
        # Передаем сессию функции get_users_from_database()
   #     users = await get_users_from_database(session)
  #      if users:
    #        response = "Список пользователей:\n"
     #       for user in users:
      #          response += f"{user}\n"
       # else:
        #    response = "В базе данных нет пользователей."
        # await message.answer(response)


async def main():
    try:
        await create_tables()
        async with async_session() as session:
            await add_new_user(session)
            user = await get_user_by_email("tommy777666ui110@gmail.com")

            if user:
                print("User found:", user)
            else:
                print("User with email 'tommy777666ui110@gmail.com' not found.")
        await main_logic()
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping the script...")
