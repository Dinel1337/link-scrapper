import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from link_scrapper.domain.models import Base, Link
from link_scrapper.domain.commands import AddLinkCommand

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s

def test_base_exists():
    assert Base is not None

def test_link_creation(session):
    link = Link(url="https://example.com", position=1)
    session.add(link)
    session.flush()
    assert link.url == "https://example.com"
    assert link.visited is False
    assert link.position == 1

def test_add_link_command():
    cmd = AddLinkCommand(url="https://test.com")
    assert cmd.url == "https://test.com"
