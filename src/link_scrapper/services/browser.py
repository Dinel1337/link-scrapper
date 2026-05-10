import requests
from playwright.sync_api import sync_playwright

def get_current_url() -> str | None:
    try:
        resp = requests.get('http://127.0.0.1:9222/json')
        pages = resp.json()
        web_pages = [p for p in pages if p.get('type') == 'page']
        return web_pages[0]['url'] if web_pages else None
    except Exception as e:
        print(f'Error getting URL: {e}')
        return None

def open_url(url: str) -> None:
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
            active_page = None
            for context in browser.contexts:
                for page in context.pages:
                    try:
                        if page.evaluate('document.visibilityState') == 'visible':
                            active_page = page
                            break
                    except:
                        pass
                if active_page:
                    break
            if active_page is None:
                # fallback – самая первая страница первого контекста
                if browser.contexts and browser.contexts[0].pages:
                    active_page = browser.contexts[0].pages[0]
            if active_page:
                active_page.goto(url)
            browser.close()
    except Exception as e:
        print(f'Error opening URL: {e}')
