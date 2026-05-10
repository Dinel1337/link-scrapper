"""Репозитории для работы с БД."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from link_scrapper.domain.models import Link
from link_scrapper.queries.link_queries import LinkDTO

class LinkCommandRepository:
    def __init__(self, session: Session):
        self._session = session

    def add_link(self, url: str) -> None:
        # Вычисляем следующий position (максимальный + 1)
        max_pos = self._session.query(func.max(Link.position)).scalar()
        next_pos = (max_pos or 0) + 1
        link = Link(url=url, position=next_pos)
        self._session.add(link)
        self._session.commit()

class LinkQueryRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_next(self) -> LinkDTO | None:
        # Берем первую непосещённую ссылку по возрастанию position
        link = (
            self._session.query(Link)
            .filter(Link.visited == False)
            .order_by(Link.position.asc())
            .first()
        )
        if not link:
            return None

        # Помечаем как прочитанную
        link.visited = True
        self._session.commit()

        return LinkDTO(id=link.id, url=link.url, visited=link.visited)
