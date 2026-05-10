import pytest
from link_scrapper.queries.link_queries import GetNextLinkQuery, LinkDTO

def test_query_creation():
    q = GetNextLinkQuery()
    assert isinstance(q, GetNextLinkQuery)

def test_dto_fields():
    dto = LinkDTO(id=1, url="https://test.com", visited=True)
    assert dto.url == "https://test.com"
