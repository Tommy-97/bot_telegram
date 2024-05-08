# run_bot.py
import asyncio
import logging

import aiohttp
from aiogram import Bot

from models import Product

API_TOKEN = '6969199222:AAFCiKI3cZbVnrhDhsyYZDpW3LBzFW36Eiw'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_message_to_user(bot, user_id, message):
    try:
        await bot.send_message(user_id, message)
        logger.info("Message sent successfully.")
    except Exception as e:
        logger.error(
            f"An error occurred while sending message to user {user_id}: {e}")


async def save_product(session, name, article, price, rating, quantity):
    try:
        # Clean and format the price value
        price_str = price
        # Remove non-numeric characters and replace comma with dot
        clean_price_str = price_str.replace('.', '').replace(',', '.')
        # Convert the cleaned string to a float value
        price_float = float(clean_price_str)

        # Create a Product object with the cleaned price
        product = Product(name=name, article=article,
                          price=price_float, rating=rating, quantity=quantity)

        # Add the product to the session
        session.add(product)
        # Commit changes and close session
        await session.commit()

        logger.info("Product added successfully!")
    except Exception as e:
        logger.error(f"An error occurred while saving product: {e}")
        # Optionally, you can rollback the session to revert any changes
        await session.rollback()


async def send_notification(bot, user_id, message_text):
    try:
        await bot.send_message(user_id, message_text)
    except Exception as e:
        logger.error(
            f"An error occurred while sending notification to user {user_id}: {e}")


async def some_other_async_function(session):
    try:
        # Your asynchronous code using the session
        async with session.begin():
            # Your database operations using the session
            ...
    except Exception as e:
        logger.error(f"An error occurred in some_other_async_function: {e}")


async def main():
    try:
        user_id = 128  # Example user ID
        message_text = "Retrieving information from the database"

        # Initialize the bot outside of the function and pass it as an argument
        bot = Bot(token=API_TOKEN)
        await send_notification(bot, user_id, message_text)

        # Initialize the session
        async with aiohttp.ClientSession() as session:
            await some_other_async_function(session)

    except Exception as e:
        logger.error(f"An error occurred in the main function: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


# if __name__ == "__main__":
 #   loop = asyncio.get_event_loop()
  #  try:
   #     loop.run_until_complete(main())
    # except KeyboardInterrupt:
    #   logger.info("Received KeyboardInterrupt, stopping the bot...")
    #  loop.stop()
