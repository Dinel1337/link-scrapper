"""Настройка подключения к БД."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from link_scrapper.domain.models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/link_scrapper"
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Создаёт все таблицы (для разработки)."""
    Base.metadata.create_all(bind=engine)
