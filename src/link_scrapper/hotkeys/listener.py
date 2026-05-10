"""Глобальные горячие клавиши."""
import keyboard
from link_scrapper.services.browser import get_current_url, open_url
from link_scrapper.domain.commands import AddLinkCommand
from link_scrapper.queries.link_queries import GetNextLinkQuery

class HotkeyListener:
    def __init__(self, command_handler, query_handler):
        self._cmd_handler = command_handler
        self._qry_handler = query_handler

    def _on_less_than(self):
        """Нажатие '<' — сохранить текущий URL."""
        url = get_current_url()
        if url:
            self._cmd_handler.handle(AddLinkCommand(url))
            print(f"Сохранено: {url}")
        else:
            print("Не удалось получить URL активной вкладки")

    def _on_yo(self):
        """Нажатие '`' (гравис) — перейти к следующей ссылке.
        Используем '`' вместо 'ё', так как keyboard надёжнее ловит физическую клавишу.
        На большинстве клавиатур клавиша 'ё' находится там же.
        """
        next_link = self._qry_handler.handle(GetNextLinkQuery())
        if next_link:
            if open_url(next_link.url):
                print(f"Перешли на: {next_link.url}")
            else:
                print("Не удалось открыть URL")
        else:
            print("Нет сохранённых ссылок")

    def start(self):
        """Запустить слушатель (блокирующий вызов)."""
        # '<' — физическая клавиша, работает в любой раскладке
        keyboard.add_hotkey('<', self._on_less_than)
        # '`' (гравис/тильда) — обычно там же, где 'ё' на русской раскладке
        keyboard.add_hotkey('`', self._on_yo)

        print("Слушатель запущен. '<' — сохранить, '`' — перейти. Ctrl+C для выхода.")
        keyboard.wait()
