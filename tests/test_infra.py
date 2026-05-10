import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from link_scrapper.domain.models import Base, Link
from link_scrapper.infra.repositories import LinkCommandRepository, LinkQueryRepository

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s

def test_add_and_get_next(session):
    cmd_repo = LinkCommandRepository(session)
    qry_repo = LinkQueryRepository(session)

    cmd_repo.add_link("https://first.com")
    cmd_repo.add_link("https://second.com")

    first = qry_repo.get_next()
    assert first.url == "https://first.com"
    assert first.visited is True

    second = qry_repo.get_next()
    assert second.url == "https://second.com"

    third = qry_repo.get_next()
    assert third is None

def test_repositories_import():
    from link_scrapper.infra import repositories
    assert repositories is not None
