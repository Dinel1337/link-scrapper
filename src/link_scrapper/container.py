"""Инициализация зависимостей."""
from link_scrapper.infra.db import SessionLocal, init_db
from link_scrapper.infra.repositories import LinkCommandRepository, LinkQueryRepository
from link_scrapper.domain.handler import CommandHandler, QueryHandler
from link_scrapper.hotkeys.listener import HotkeyListener

def create_app():
    # Инициализация БД (создание таблиц)
    init_db()

    # Создаём репозитории с одной сессией на старт (в реальном коде лучше фабрика)
    session = SessionLocal()
    cmd_repo = LinkCommandRepository(session)
    qry_repo = LinkQueryRepository(session)

    # Обработчики
    cmd_handler = CommandHandler(cmd_repo)
    qry_handler = QueryHandler(qry_repo)

    # Слушатель
    listener = HotkeyListener(cmd_handler, qry_handler)
    return listener
