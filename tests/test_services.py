import pytest
from unittest.mock import patch, MagicMock
from link_scrapper.services.browser import get_current_url, open_url

@patch("link_scrapper.services.browser.sync_playwright")
def test_get_current_url(mock_playwright):
    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_context = MagicMock()
    mock_context.pages = [mock_page]
    mock_browser.contexts = [mock_context]
    mock_playwright.return_value.__enter__.return_value.chromium.connect_over_cdp.return_value = mock_browser

    url = get_current_url()
    assert url == "https://example.com"

@patch("link_scrapper.services.browser.sync_playwright")
def test_open_url(mock_playwright):
    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_context = MagicMock()
    mock_context.pages = [mock_page]
    mock_browser.contexts = [mock_context]
    mock_playwright.return_value.__enter__.return_value.chromium.connect_over_cdp.return_value = mock_browser

    result = open_url("https://newlink.com")
    assert result is True
    mock_page.goto.assert_called_once_with("https://newlink.com")
