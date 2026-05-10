import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from link_scrapper.domain.models import Base, Link
from link_scrapper.infra.repositories import LinkCommandRepository, LinkQueryRepository

@pytest.fixture
def engine():
    return create_engine("sqlite:///:memory:")

@pytest.fixture
def session(engine):
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
    Base.metadata.drop_all(engine)

@pytest.fixture
def cmd_repo(session):
    return LinkCommandRepository(session)

@pytest.fixture
def qry_repo(session):
    return LinkQueryRepository(session)

def test_add_unique_link(cmd_repo):
    assert cmd_repo.add("https://new.com") == True
    assert cmd_repo.add("https://new.com") == False

def test_load_batch_after(qry_repo, session):
    for i in range(15):
        session.add(Link(url=f"https://link{i}.com"))
    session.commit()
    # Первая партия после id=0
    batch = qry_repo.load_batch_after(0, 10)
    assert len(batch) == 10
    assert batch[0].url == "https://link0.com"
    assert batch[-1].url == "https://link9.com"
    # Вторая партия после последнего id (9)
    last_id = batch[-1].id
    batch2 = qry_repo.load_batch_after(last_id, 10)
    assert len(batch2) == 5
    assert batch2[0].url == "https://link10.com"

def test_load_only_unvisited(qry_repo, session):
    session.add(Link(url="https://vis.com", visited=True))
    session.add(Link(url="https://unvis.com", visited=False))
    session.commit()
    batch = qry_repo.load_batch_after(0, 10)
    assert len(batch) == 1
    assert batch[0].url == "https://unvis.com"

def test_mark_visited(qry_repo, session):
    link = Link(url="https://tovisit.com")
    session.add(link)
    session.commit()
    qry_repo.mark_visited(link)
    assert link.visited == True
