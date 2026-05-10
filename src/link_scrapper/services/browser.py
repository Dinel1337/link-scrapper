import requests

def get_current_url() -> str | None:
    """Возвращает URL активной вкладки Edge."""
    try:
        resp = requests.get("http://127.0.0.1:9222/json")
        pages = resp.json()
        web_pages = [p for p in pages if p.get("type") == "page"]
        if web_pages:
            return web_pages[0]["url"]
    except Exception as e:
        print(f"Ошибка получения URL: {e}")
    return None

def open_url(url: str) -> None:
    """Открывает URL в активной вкладке через Playwright CDP."""
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            pages = browser.contexts[0].pages if browser.contexts else []
            if pages:
                pages[-1].goto(url)
                browser.close()
    except Exception as e:
        print(f"Ошибка открытия URL: {e}")
