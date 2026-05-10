import pytest
from link_scrapper.queries.link_queries import GetNextLinkQuery

def test_get_next_link_query():
    q = GetNextLinkQuery()
    assert isinstance(q, GetNextLinkQuery)
