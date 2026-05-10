import keyboard
from link_scrapper.container import container
from link_scrapper.domain.commands import AddLinkCommand
from link_scrapper.queries.link_queries import GetNextLinkQuery
from link_scrapper.services.browser import get_current_url, open_url

def on_save():
    url = get_current_url()
    if url:
        added = container.command_handler.handle(AddLinkCommand(url))
        if added:
            print(f"✓ Сохранена: {url}")
        else:
            print(f"→ Уже есть: {url}")
    else:
        print("Не удалось получить URL активной вкладки")

def on_next():
    next_url = container.query_handler.handle(GetNextLinkQuery())
    if next_url:
        open_url(next_url)
        print(f"→ Переход: {next_url}")
    else:
        print("Все ссылки просмотрены или список пуст")

keyboard.add_hotkey(',', on_save)
keyboard.add_hotkey('`', on_next)

print("Горячие клавиши: ',' — сохранить текущий URL, '`' — следующая ссылка.")
print("Для выхода нажмите Ctrl+C")
keyboard.wait()
