import requests

def get_active_url():
    response = requests.get("http://127.0.0.1:9222/json")
    pages = response.json()
    web_pages = [p for p in pages if p.get("type") == "page"]
    if web_pages:
        return web_pages[0]["url"]
    return None

print(f"Активная вкладка: {get_active_url()}")