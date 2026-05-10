"""Запросы и DTO."""
from dataclasses import dataclass
from typing import Optional

class GetNextLinkQuery:
    """Запрос на получение следующей непосещённой ссылки."""

@dataclass
class LinkDTO:
    id: int
    url: str
    visited: bool
