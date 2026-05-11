import requests

def get_current_url() -> str | None:
    try:
        resp = requests.get('http://127.0.0.1:9222/json', timeout=2)
        pages = resp.json()
        web_pages = [p for p in pages if p.get('type') == 'page']
        return web_pages[0]['url'] if web_pages else None
    except Exception as e:
        print(f'Error getting URL: {e}')
        return None

def open_url(browser, url: str) -> None:
    try:
        # Определяем активную вкладку через HTTP (быстро)
        resp = requests.get('http://127.0.0.1:9222/json', timeout=2)
        pages = resp.json()
        web_pages = [p for p in pages if p.get('type') == 'page']
        if not web_pages:
            print('No open pages found')
            return
        active_url = web_pages[0]['url']

        # Ищем страницу с таким же URL
        target_page = None
        for context in browser.contexts:
            for page in context.pages:
                if page.url == active_url:
                    target_page = page
                    break
            if target_page:
                break

        # Fallback
        if target_page is None and browser.contexts:
            for context in browser.contexts:
                if context.pages:
                    target_page = context.pages[0]
                    break

        if target_page:
            target_page.goto(url)
        else:
            print('No page available for navigation')
    except Exception as e:
        print(f'Error opening URL: {e}')
