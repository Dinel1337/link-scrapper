"""Взаимодействие с браузером через CDP."""
from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:9222"

def get_current_url() -> str | None:
    """Получить URL активной вкладки."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(CDP_URL)
            contexts = browser.contexts
            if not contexts:
                return None
            pages = contexts[0].pages
            if not pages:
                return None
            url = pages[-1].url
            browser.close()
            return url
    except Exception as e:
        print(f"Error getting URL: {e}")
        return None

def open_url(url: str) -> bool:
    """Открыть URL в текущей вкладке."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(CDP_URL)
            contexts = browser.contexts
            if not contexts:
                return False
            pages = contexts[0].pages
            if not pages:
                return False
            pages[-1].goto(url)
            browser.close()
            return True
    except Exception as e:
        print(f"Error opening URL: {e}")
        return False
