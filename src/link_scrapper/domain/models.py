from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    visited = Column(Boolean, default=False, nullable=False)
    position = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Link(id={self.id}, url={self.url}, visited={self.visited})>"
