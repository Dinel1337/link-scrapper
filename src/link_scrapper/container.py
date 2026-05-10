from functools import lru_cache
from link_scrapper.infra.db import get_session, init_db
from link_scrapper.infra.repositories import LinkCommandRepository, LinkQueryRepository
from link_scrapper.domain.handler import CommandHandler, QueryHandler

class Container:
    def __init__(self, state_file="state.json"):
        self._session = None
        self.state_file = state_file

    @property
    def session(self):
        if self._session is None:
            self._session = next(get_session())
        return self._session

    @property
    @lru_cache(maxsize=1)
    def link_command_repo(self) -> LinkCommandRepository:
        return LinkCommandRepository(self.session)

    @property
    @lru_cache(maxsize=1)
    def link_query_repo(self) -> LinkQueryRepository:
        return LinkQueryRepository(self.session)

    @property
    @lru_cache(maxsize=1)
    def command_handler(self) -> CommandHandler:
        return CommandHandler(self.link_command_repo)

    @property
    @lru_cache(maxsize=1)
    def query_handler(self) -> QueryHandler:
        return QueryHandler(self.link_query_repo, state_file=self.state_file)

    def close(self):
        if self._session:
            self._session.close()
            self._session = None

container = Container()
