from sqlalchemy import select
from sqlalchemy.orm import Session
from link_scrapper.domain.models import Link

class LinkCommandRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, url: str) -> bool:
        stmt = select(Link).where(Link.url == url)
        existing = self.session.execute(stmt).scalar_one_or_none()
        if existing is not None:
            return False
        link = Link(url=url)
        self.session.add(link)
        self.session.commit()
        return True

class LinkQueryRepository:
    def __init__(self, session: Session):
        self.session = session

    def load_batch_after(self, last_id: int = 0, limit: int = 10) -> list[Link]:
        """Загружает непосещённые ссылки с id > last_id, не более limit штук."""
        stmt = (
            select(Link)
            .where(Link.visited == False, Link.id > last_id)
            .order_by(Link.id)
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def mark_visited(self, link: Link) -> None:
        link.visited = True
        self.session.commit()
