from link_scrapper.domain.commands import AddLinkCommand, DeleteLinkCommand
from link_scrapper.queries.link_queries import GetNextLinkQuery
from link_scrapper.infra.repositories import LinkCommandRepository, LinkQueryRepository

class CommandHandler:
    def __init__(self, repo: LinkCommandRepository):
        self.repo = repo

    def handle(self, cmd) -> bool:
        if isinstance(cmd, AddLinkCommand):
            return self.repo.add(cmd.url)
        elif isinstance(cmd, DeleteLinkCommand):
            return self.repo.delete(cmd.url)
        else:
            raise ValueError(f"Unknown command: {cmd}")

class QueryHandler:
    def __init__(self, repo: LinkQueryRepository, reverse=False):
        self.repo = repo
        self.reverse = reverse

    def handle(self, query: GetNextLinkQuery) -> str | None:
        if self.reverse:
            link = self.repo.get_next_unvisited_reverse()
        else:
            link = self.repo.get_next_unvisited()
        return link.url if link else None
