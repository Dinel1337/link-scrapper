import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from link_scrapper.domain.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///link_scrapper.db")
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
