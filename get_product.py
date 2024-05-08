# get_product.py
import logging

import aiohttp

# Создание объекта логгера
logger = logging.getLogger(__name__)


async def get_product_info_from(article, session, save_product):
    url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={article}{session}{save_product} "
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                if data:
                    product_data = data.get('data', {}).get('products', [])
                    if product_data:
                        # Assume there is only one product
                        product = product_data[0]
                        name = product.get('name')
                        article = product.get('article')
                        price = product.get('price')
                        rating = product.get('rating')
                        quantity = product.get('quantity')
                        return {
                            'name': name,
                            'article': article,
                            'price': price,
                            'rating': rating,
                            'quantity': quantity
                        }
                    else:
                        return None
                else:
                    return None
    except aiohttp.ClientResponseError as exc:
        logger.error(f"HTTP-ошибка: {exc}")
        return f"HTTP-ошибка: {exc}"
    except aiohttp.ClientError as exc:
        logger.error(f"Ошибка клиента: {exc}")
        return f"Ошибка клиента: {exc}"
    except aiohttp.InvalidURL as exc:
        logger.error(f"Некорректный URL: {exc}")
        return f"Некорректный URL: {exc}"
    except aiohttp.ServerDisconnectedError as exc:
        logger.error(f"Ошибка отключения сервера: {exc}")
        return f"Ошибка отключения сервера: {exc}"
    except aiohttp.ContentTypeError as exc:
        logger.error(f"Ошибка типа содержимого: {exc}")
        return f"Ошибка типа содержимого: {exc}"
    except Exception as e:
        logger.error(f"Ошибка при получении информации о товаре: {e}")
        return f"Произошла ошибка при получении информации о товаре. Пожалуйста, попробуйте позже."
