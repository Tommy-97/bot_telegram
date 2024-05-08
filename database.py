# database.py
import asyncio
import email
import logging
import time
import types
# from datetime import datetime
import datetime
from itertools import product
import re
import aiosqlite
from aiogram.types import Message
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from base import Base, send_notification
from config import SQLALCHEMY_URL, send_message_to_user
from db_utils import async_session
from get_product import get_product_info_from as get_product_info
from models import Product, User
from run_bot import save_product

# from sqlite3 import IntegrityError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SQLALCHEMY_URL = "sqlite+aiosqlite:///F:/SQLete/Auto_base.db"


# Создаем подключение к базе данных
engine = create_async_engine(SQLALCHEMY_URL, echo=True, future=True, connect_args={
                             "check_same_thread": False})
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, future=True)


async def create_tables():
    async with aiosqlite.connect("Auto_base.db") as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              name TEXT,
                              email TEXT UNIQUE,
                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )''')
        await db.commit()


async def add_user(name, email):
    try:
        async with aiosqlite.connect("Auto_base.db") as connection:
            cursor = await connection.execute('SELECT * FROM users WHERE email = ?', (email,))
            existing_user = await cursor.fetchone()
            if existing_user:
                print("User with this email already exists.")
                return
            await connection.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
            await connection.commit()
            print("User added successfully!")
    except Exception as e:
        print(f"Failed to add user: {e}")


async def get_user_by_email(email):
    try:
        async with aiosqlite.connect("Auto_base.db") as db:
            cursor = await db.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = await cursor.fetchone()
            return user
    except Exception as e:
        print(f"An error occurred while getting user by email: {e}")
        # return None


async def add_new_user(name, email):
    try:
        async with aiosqlite.connect("Auto_base.db") as db:
            await db.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
            await db.commit()
            print("User added successfully!")
    except IntegrityError:
        print("User with this email already exists.")
    except Exception as e:
        print(f"Failed to add user: {e}")


async def add_new_user_by_email(session, email):
    try:
        existing_user = await get_user_by_email(email)
        if existing_user:
            print(f"User with email '{email}' already exists.")
        else:
            await add_new_user(name="Default Name", email=email)
            print(f"New user with email '{email}' added successfully.")
    except Exception as e:
        print(f"An error occurred while adding a new user by email: {e}")


async def add_new_user_with_async_session(name, email):
    try:
        async with async_session() as session:
            user = User(name=name, email=email)
            session.add(user)
            await session.commit()
            print("User added successfully!")
    except IntegrityError:
        print("User with this email already exists.")
    except Exception as e:
        print(f"Failed to add user: {e}")


async def main():
    await create_tables()
    await add_new_user('Pollhhh', 'tommyk7hhhh7780ui110@gmail.com')
    user = await get_user_by_email('h7780ui110@gmail.com')
    print(user)

if __name__ == '__main__':
    asyncio.run(main())


async def main():
    article = "123456"
    async with async_session() as session:
        product_info = await get_product_info(article, session, save_product)
        if product_info:
            print("Product info:", product_info)
        else:
            print("Product not found.")

# Запуск асинхронной функции main
asyncio.run(main())


async def get_user_info_by_email(session, email):
    try:
        result = await session.execute(select(User).filter(User.email == email))
        user = await result.scalar_one_or_none()
        if user is None:
            print("User not found.")
        return user
    except Exception as e:
        print(
            f"An error occurred while fetching user information by email: {e}")


async def get_product_info(article, session, save_product, message_object, bot, user_id):
    try:
        product_info = {
            'name': 'Какой-то беганутый продукт!',
            'article': 123456,
            'price': '20000руб',
            'rating': 'в топе',
            'quantity': '1000пар'
        }

        price_string = "20000руб"
        # Оставляем только цифры и точку
        clean_price_string = ''.join(
            filter(str.isdigit, price_string))  # Получаем '20000'
        if '.' in price_string:
            clean_price_string += '.'  # Добавляем точку в конец, если она была в исходной строке
        # Преобразуем в число с плавающей точкой
        price = float(clean_price_string)

        # Преобразование числа в дату
        timestamp = time.time()  # Текущее время в секундах с начала эпохи Unix
        date = datetime.datetime.fromtimestamp(
            timestamp)  # Преобразование в объект datetime

        # Добавление даты в информацию о продукте
        product_info['timestamp'] = date

        # Вызовите save_product_func для сохранения информации о продукте
        await save_product(session, **product_info)

        # Отправьте информацию о продукте пользователю
        message_text = (
            f"Информация о продукте:\n"
            f"Название: {product_info['name']}\n"
            f"Цена: {product_info['price']}\n"
            f"Рейтинг: {product_info['rating']}\n"
            f"Количество: {product_info['quantity']}\n"
            f"Дата: {date}"
        )
        await bot.send_message(user_id, message_text)

        return product_info
    except ValueError as ve:
        # Возникает, если не удается преобразовать строку в число
        logger.error(
            f"Произошла ошибка при получении информации о продукте из базы данных: {ve}")
        print("Clean price string:", clean_price_string)
    except Exception as e:
        # Обрабатываем любые другие исключения и логируем их
        logger.error(
            f"Произошла ошибка при получении информации о продукте из базы данных: {e}")
        return None


async def get_product_info_command(message, bot):
    article = message.text.split()[-1]
    async with async_session() as session:
        product_info = await get_product_info(article, session, save_product, message, bot, message.from_user.id)
        if product_info:
            print("Product info:", product_info)
            await save_product(session, **product_info)
        else:
            print("Product not found.")
            # Отправляем сообщение пользователю о том, что продукт не найден
            await bot.send_message(message.from_user.id, "Product not found. Please try again.")


async def process_product_info(product_info, session, save_product_func):

    required_fields = ['name', 'article', 'price', 'rating', 'quantity']
    if all(field in product_info for field in required_fields):
        # Все необходимые поля присутствуют, можно сохранять продукт
        name = product_info.get('name')
        article = product_info.get('article')
        price = product_info.get('price')
        rating = product_info.get('rating')
        quantity = product_info.get('quantity')

        await save_product_func(session, name, article, price, rating, quantity)
    else:
        # Не все необходимые поля присутствуют, выводим сообщение об ошибке
        print("Error: Missing required fields in product_info")


async def get_user_info_by_email(session, email):
    try:
        result = await session.execute(select(User).filter(User.email == email))
        user = await result.scalar_one_or_none()
        if user is None:
            print("User not found.")
        return user
    except Exception as e:
        # Обрабатываем любые исключения и логируем их
        logger.error(
            f"An error occurred while fetching user information by email {e}")
        return None


async def add_user_and_email(session, name, email):
    if session is None:
        print("Session is None")
        return

    try:
        async with session.begin():
            new_user = User(name=name, email=email)
            session.add(new_user)
    except Exception as e:
        print(f"Failed to add user: {e}")
    else:
        await session.commit()
        print("User added successfully!")


async def check_product_status_and_notify():
    while True:
        try:
            products = await get_all_products()
            for product in products:
                if product.status == 'out_of_stock':
                    await send_notification(product.owner_id, f"Product '{product.name}' is out of stock.")
                elif product.status == 'low_stock':
                    await send_notification(product.owner_id, f"Product '{product.name}' is running low in stock.")
        except Exception as e:
            # Log the error and continue the loop
            logger.error(
                f"An error occurred while checking product status: {e}")
        finally:
            # Sleep for 24 hours before checking again
            await asyncio.sleep(24 * 60 * 60)


async def fetch_information_from_db(session):
    try:
        async with session as s:
            query_result = await s.execute(select(User))
            information = query_result.scalars().all()
            print("Information fetched successfully")
            return information
    except Exception as e:
        # Обрабатываем любые исключения и логируем их
        logger.error(
            f"An error occurred while fetching information from the database: {e}")
        return None


async def some_function_where_you_call_fetch_information():
    try:
        async with async_session() as session:
            information = await fetch_information_from_db(session)
            if information:
                print("Fetched information:", information)
            else:
                print("No information available from the database.")
    except Exception as e:
        print(f"An error occurred: {e}")


async def get_users_from_database(session):
    try:
        query = await session.execute(select(User))
        users = query.scalars().all()
        return [str(user) for user in users]
    except Exception as e:
        # Обрабатываем любые исключения и логируем их
        logger.error(
            f"An error occurred while fetching users from the database: {e}")
        return None


async def get_all_products(session):
    try:
        query = await session.execute(select(Product))
        return query.scalars().all()
    except Exception as e:
        # Обрабатываем любые исключения и логируем их
        logger.error(f"An error occurred while fetching all products: {e}")
        return None


async def get_product_price(session, article):
    try:
        product = await session.execute(select(Product).where(Product.article == article))
        product = await product.fetchone()
        return product.price if product else None

    except Exception as e:
        # Обрабатываем любые исключения и логируем их
        logger.error(f"An error occurred while fetching product price: {e}")
        return None


async def fetch_product_price(article):
    try:
        async with async_session() as session:
            price = await get_product_price(session, article)
            if price is not None:
                print(f"Price of product {article}: {price}")
            else:
                print(f"Product {article} not found or price is not available")
    except Exception as e:
        # Обрабатываем любые исключения и логируем их
        logger.error(f"An error occurred while fetching product price: {e}")
        return None


async def get_message_from_database(message_id):
    try:
        async with async_session() as session:
            message = await session.execute(select(Message).filter(Message.id == message_id))
            message = await message.fetchone()
            return message
    except Exception as e:
        # Обрабатываем любые исключения и логируем их
        logger.error(
            f"An error occurred while fetching message from the database: {e}")
        return None


async def fetch_and_print_message():
    message_id = 123
    message_from_db = await get_message_from_database(message_id)
    if message_from_db:
        print("Message:", message_from_db.text)
    else:
        print("Message not found in the database.")


async def main():
    await fetch_and_print_message()

asyncio.run(main())


# async def get_product_info_from_db(article, session, save_product):
#   try:
#      async with aiosqlite.connect("Auto_base.db") as db:
#         cursor = await db.execute('''SELECT * FROM products WHERE article = ?''', (article,))
#        product = await cursor.fetchone()
#      if product:
#          product_info = {
#              'name': product[1],
#             'article': product[2],
#            'rating': product[4],
#       }
#        return product_info
#    else:
#       return None
# except Exception as e:
#    return None


# async def get_product_info(article, session, save_product, message_object, bot, user_id):
# #  try:
#    # Your code to fetch product info here
#   product_info = {
#      'name': 'Какой то продукт!',
#     'article': 123456,
#    'price': 10.99,
#   'rating': 4.5,
#  'quantity': 100
#     }
# Call save_product_func to save the product info
#    await save_product(session, **product_info)

# Send product info to the user
#   message_text = f"Product info:\nName: {product_info['name']}\nPrice: {product_info['price']}#\nRating: {product_info['rating']}\nQuantity: {product_info['quantity']}"
#   await message_object.send_message(user_id, message_text)

#  return product_info
# except Exception as e:
#   print(f"An error occurred while fetching product information: {e}")
#  return None


# async def get_product_info(article, session, save_product):
#   try:
#      product_info = await get_product_info_from_db(article, session, save_product)
#     if product_info:
# Save the product info
#        await save_product(session, **product_info)
#       return product_info
#  else:
#     print("Product not found.")
#      return None
# except Exception as e:
#   print(f"An error occurred while fetching product information: {e}")
#  return None


# async def get_product_info(article, session, save_product, message_object, bot, user_id):
#   try:
#      product_info = await get_product_info_from_db(article, session)
#     if product_info:
# Отправляем информацию о продукте пользователю
#        message_text = (
#           f"Информация о продукте:\n"
#          f"Название: {product_info['name']}\n"
#         f"Цена: {product_info['price']}\n"
#        f"Рейтинг: {product_info['rating']}\n"
#       f"Количество: {product_info['quantity']}"
#  )
# Используем метод send_message у объекта bot для отправки сообщения
#  await bot.send_message(user_id, message_text)
# return product_info
# else:
# Если продукт не найден, отправляем сообщение об этом
#   await message_object.send_message(user_id, "Продукт не найден.")
#  return None
# except Exception as e:
# Обрабатываем любые исключения и логируем их
# logger.error(f"Произошла ошибка при получении информации о продукте: {e}")
# return None


# async def get_product_info_from_db(article, session):
#   try:
# Выполняем запрос к базе данных для получения информации о продукте
#      result = await session.execute(select(Product).filter(Product.article == article))
#     product = await result.fetchall()

#    if product:
#       product_info = {
#          'name': product,
#         'article': 1222,
#        'price': 00,
#       'rating': 33,
#      'quantity': 10/10
# }
# return product_info
# else:
#   return None
