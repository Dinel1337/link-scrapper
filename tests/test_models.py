import pytest
from link_scrapper.domain.models import Base, Link
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

@pytest.fixture
def engine():
    return create_engine("sqlite:///:memory:")

@pytest.fixture
def session(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
    Base.metadata.drop_all(engine)

def test_link_creation(session):
    link = Link(url="https://example.com")
    session.add(link)
    session.commit()
    assert link.id is not None
    assert link.url == "https://example.com"
    assert not link.visited
    assert link.created_at is not None

def test_link_unique_constraint(session):
    session.add(Link(url="https://unique.com"))
    session.commit()
    with pytest.raises(Exception):
        session.add(Link(url="https://unique.com"))
        session.commit()
    session.rollback()
