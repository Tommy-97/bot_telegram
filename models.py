# models.py
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from base import Base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}', created_at='{self.created_at}')>"


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    article = Column(String, unique=True, index=True)  # Добавьте этот столбец
    price = Column(Float)
    rating = Column(Float)
    quantity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)  # Добавляем поле для хранения времени создания
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Добавляем поле для хранения времени обновления


class RequestHistory(Base):
    __tablename__ = 'request_history'
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    product_article = Column(String)


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


