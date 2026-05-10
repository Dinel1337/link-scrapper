"""Репозитории для работы с БД."""
from . import connect_db
from link_scrapper.domain.models import Link
from link_scrapper.queries.link_queries import LinkDTO

class LinkRepository():
    