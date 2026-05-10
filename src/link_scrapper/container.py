from functools import lru_cache
from link_scrapper.infra.db import SessionLocal, init_db
from link_scrapper.infra.repositories import LinkCommandRepository, LinkQueryRepository
from link_scrapper.domain.handler import CommandHandler, QueryHandler
from link_scrapper.hotkeys.listener import Listener

class Container:
    def __init__(self, state_file='state.json'):
        self.session = SessionLocal()
        self.state_file = state_file

    @property
    @lru_cache(maxsize=1)
    def link_command_repo(self):
        return LinkCommandRepository(self.session)

    @property
    @lru_cache(maxsize=1)
    def link_query_repo(self):
        return LinkQueryRepository(self.session)

    @property
    @lru_cache(maxsize=1)
    def command_handler(self):
        return CommandHandler(self.link_command_repo)

    @property
    @lru_cache(maxsize=1)
    def query_handler(self):
        return QueryHandler(self.link_query_repo, state_path=self.state_file)

    def close(self):
        self.session.close()

def create_app(state_file='state.json'):
    init_db()
    container = Container(state_file=state_file)
    listener = Listener(
        command_handler=container.command_handler,
        query_handler=container.query_handler
    )
    return listener
