#env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
# Этот блок импортирует ваши модели данных из вашего приложения
from models import models

# Здесь мы импортируем конфигурацию базы данных из alembic.ini
config = context.config

# Устанавливаем объект подключения к базе данных
target_metadata = models.Base.metadata

# Это гарантирует, что logging будет настроен как указано в alembic.ini
fileConfig(config.config_file_name)

# Создаем объект подключения к базе данных из нашего alembic.ini
# Для этого нам нужно получить URL подключения к базе данных из конфигурации
# и передать его в функцию engine_from_config
# Вам нужно настроить секцию [alembic] в вашем alembic.ini для вашей базы данных
# Например:
# [alembic]
# sqlalchemy.url = postgresql://user:password@localhost/mydatabase
db_url = config.get_main_option("sqlalchemy.url")
engine = engine_from_config(
    {"sqlalchemy.url": db_url},
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)

# Настраиваем Alembic для использования созданного подключения к базе данных
context.configure(
    connection=engine.connect(), target_metadata=target_metadata
)
