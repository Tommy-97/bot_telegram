# db_utils.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///F:/SQLete/Auto_base.db"

engine = create_async_engine(DATABASE_URL, echo=True)

# Creating an asynchronous session class
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, future=True
)
