import json
from pathlib import Path
from link_scrapper.domain.commands import AddLinkCommand, DeleteLinkCommand
from link_scrapper.queries.link_queries import GetNextLinkQuery
from link_scrapper.infra.repositories import LinkCommandRepository, LinkQueryRepository
from link_scrapper.domain.models import Link

STATE_FILE = "state.json"

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
    def __init__(self, repo: LinkQueryRepository, state_path: str = STATE_FILE):
        self.repo = repo
        self.state_path = Path(state_path)
        self.cache: list[Link] = []
        self.last_visited_id: int = 0
        self.current_index: int = 0
        self._load_state()

    def _load_state(self):
        if self.state_path.exists():
            data = json.loads(self.state_path.read_text())
            self.last_visited_id = data.get("last_visited_id", 0)
            saved_index = data.get("current_index", 0)
        else:
            self.last_visited_id = 0
            saved_index = 0

        self.cache = self.repo.load_batch_after(self.last_visited_id, limit=10)
        self.current_index = saved_index if saved_index < len(self.cache) else 0
        self._save_state()

    def _save_state(self):
        self.state_path.write_text(json.dumps({
            "last_visited_id": self.last_visited_id,
            "current_index": self.current_index
        }))

    def _ensure_cache_has_items(self):
        if len(self.cache) - self.current_index <= 2:
            last_cached_id = self.cache[-1].id if self.cache else self.last_visited_id
            new_links = self.repo.load_batch_after(last_cached_id, limit=10)
            if new_links:
                self.cache.extend(new_links)
                self._save_state()

    def handle(self, query: GetNextLinkQuery) -> str | None:
        self._ensure_cache_has_items()
        if self.current_index >= len(self.cache):
            return None
        link = self.cache[self.current_index]
        self.repo.mark_visited(link)
        self.last_visited_id = link.id
        self.current_index += 1
        self._save_state()
        self._ensure_cache_has_items()
        return link.url
