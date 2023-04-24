import os

import pytest

from database import database

# Устанавливаем `os.environ`, чтобы использовать тестовую БД
os.environ['TESTING'] = 'True'

from alembic import command
from alembic.config import Config

from sqlalchemy_utils import create_database, drop_database


@pytest.fixture(scope="module")
def temp_db():
    create_database(database.TEST_SQLALCHEMY_DATABASE_URL) # Создаем БД
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini")) # Загружаем конфигурацию alembic
    command.upgrade(alembic_cfg, "head") # выполняем миграции

    try:
        yield databse.TEST_SQLALCHEMY_DATABASE_URL
    finally:
        drop_database(database.TEST_SQLALCHEMY_DATABASE_URL) # удаляем БД