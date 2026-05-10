from unittest.mock import patch, MagicMock
from link_scrapper.services.browser import get_current_url

def test_get_current_url_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {"type": "page", "url": "https://active.com", "title": "Active"},
        {"type": "page", "url": "https://bg.com", "title": "Background"},
        {"type": "worker", "url": "https://worker.com"},
    ]
    with patch("requests.get", return_value=mock_resp):
        assert get_current_url() == "https://active.com"

def test_get_current_url_no_pages():
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {"type": "worker", "url": "https://worker.com"}
    ]
    with patch("requests.get", return_value=mock_resp):
        assert get_current_url() is None

def test_get_current_url_exception():
    with patch("requests.get", side_effect=Exception("conn refused")):
        assert get_current_url() is None
