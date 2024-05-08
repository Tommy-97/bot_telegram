#base.py

import asyncio

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RequestHistory(Base):
    __tablename__ = 'request_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    timestamp = Column(DateTime)
    product_article = Column(String)

    def __repr__(self):
        return f"<RequestHistory(user_id={self.user_id}, timestamp={self.timestamp}, product_article={self.product_article})>"

async def send_notification(user_id, message):
    # Ваша реальная логика отправки уведомлений здесь
    print(f"Отправка уведомления пользователю с ID {user_id}: {message}")
    await asyncio.sleep(1)  # Имитация задержки отправки
    print("Уведомление успешно отправлено.")
