"""Обработчики команд и запросов."""
from typing import Optional
from link_scrapper.domain.commands import AddLinkCommand
from link_scrapper.queries.link_queries import GetNextLinkQuery, LinkDTO
from link_scrapper.infra.repositories import LinkCommandRepository, LinkQueryRepository

class CommandHandler:
    def __init__(self, command_repo: LinkCommandRepository):
        self._repo = command_repo

    def handle(self, command: AddLinkCommand) -> None:
        self._repo.add_link(command.url)

class QueryHandler:
    def __init__(self, query_repo: LinkQueryRepository):
        self._repo = query_repo

    def handle(self, query: GetNextLinkQuery) -> Optional[LinkDTO]:
        return self._repo.get_next()
