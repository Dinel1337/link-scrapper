from sqlalchemy import select, update
from sqlalchemy.orm import Session
from link_scrapper.domain.models import Link

class LinkCommandRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, url: str) -> bool:
        stmt = select(Link).where(Link.url == url)
        existing = self.session.execute(stmt).scalar_one_or_none()
        if existing is not None:
            if existing.visited:
                existing.visited = False
                self.session.commit()
            return False
        link = Link(url=url)
        self.session.add(link)
        self.session.commit()
        return True

    def delete(self, url: str) -> bool:
        stmt = select(Link).where(Link.url == url)
        link = self.session.execute(stmt).scalar_one_or_none()
        if link is None:
            return False
        self.session.delete(link)
        self.session.commit()
        return True

    def delete_all(self) -> int:
        count = self.session.query(Link).delete()
        self.session.commit()
        return count

    def reset_all_visited(self) -> int:
        stmt = update(Link).values(visited=False)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount

    def set_visited(self, url: str, visited: bool) -> bool:
        stmt = select(Link).where(Link.url == url)
        link = self.session.execute(stmt).scalar_one_or_none()
        if link is None:
            return False
        link.visited = visited
        self.session.commit()
        return True

class LinkQueryRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_next_unvisited(self) -> Link | None:
        stmt = select(Link).where(Link.visited == False).order_by(Link.id).limit(1)
        link = self.session.execute(stmt).scalar_one_or_none()
        if link is not None:
            link.visited = True
            self.session.commit()
        return link

    def get_next_unvisited_reverse(self) -> Link | None:
        stmt = select(Link).where(Link.visited == False).order_by(Link.id.desc()).limit(1)
        link = self.session.execute(stmt).scalar_one_or_none()
        if link is not None:
            link.visited = True
            self.session.commit()
        return link
