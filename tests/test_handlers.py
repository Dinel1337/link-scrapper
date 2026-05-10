import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from link_scrapper.domain.models import Base, Link
from link_scrapper.domain.commands import AddLinkCommand
from link_scrapper.queries.link_queries import GetNextLinkQuery
from link_scrapper.domain.handler import CommandHandler, QueryHandler
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
def cmd_handler(session):
    return CommandHandler(LinkCommandRepository(session))

@pytest.fixture
def qry_handler(session, tmp_path):
    state = tmp_path / "state.json"
    for i in range(25):
        session.add(Link(url=f"https://link{i}.com"))
    session.commit()
    return QueryHandler(LinkQueryRepository(session), str(state))

def test_add_command(cmd_handler):
    assert cmd_handler.handle(AddLinkCommand("https://new.com"))
    assert not cmd_handler.handle(AddLinkCommand("https://new.com"))

def test_query_handler_caching(qry_handler):
    url = qry_handler.handle(GetNextLinkQuery())
    assert url == "https://link0.com"
    url = qry_handler.handle(GetNextLinkQuery())
    assert url == "https://link1.com"

def test_query_handler_state_persistence(session, tmp_path):
    state = tmp_path / "state.json"
    # Создаём 15 ссылок
    for i in range(15):
        session.add(Link(url=f"https://link{i}.com"))
    session.commit()
    # Вручную помечаем первые 5 как посещённые (id 1..5)
    links = session.query(Link).order_by(Link.id).all()
    for l in links[:5]:
        l.visited = True
    session.commit()
    # last_visited_id должен быть = 5 (последний посещённый)
    state.write_text(json.dumps({"last_visited_id": 5, "current_index": 0}))
    handler = QueryHandler(LinkQueryRepository(session), str(state))
    # Первая ссылка после id=5 (непосещённая) – это link5 (id=6)
    next_url = handler.handle(GetNextLinkQuery())
    assert next_url == "https://link5.com"
    # Проверяем, что last_visited_id обновился
    assert handler.last_visited_id == 6  # id ссылки link5

def test_auto_load_more(session, tmp_path):
    state = tmp_path / "state.json"
    # 10 ссылок
    for i in range(10):
        session.add(Link(url=f"https://link{i}.com"))
    session.commit()
    handler = QueryHandler(LinkQueryRepository(session), str(state))
    # Проходим 8 штук
    for _ in range(8):
        handler.handle(GetNextLinkQuery())
    # Кэш всё ещё 10 элементов
    assert len(handler.cache) == 10
    # Следующая – девятая
    url = handler.handle(GetNextLinkQuery())
    assert url == "https://link8.com"
    # Десятая
    url = handler.handle(GetNextLinkQuery())
    assert url == "https://link9.com"
    # Больше нет
    url = handler.handle(GetNextLinkQuery())
    assert url is None
