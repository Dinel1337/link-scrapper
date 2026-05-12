import keyboard
import threading
import time
from link_scrapper.domain.commands import AddLinkCommand, DeleteLinkCommand
from link_scrapper.queries.link_queries import GetNextLinkQuery
from link_scrapper.services.browser import get_current_url, open_url
from link_scrapper.services.templates import generate_message
from playwright.sync_api import sync_playwright

class BrowserHistory:
    def __init__(self):
        self.back_stack = []
        self.forward_stack = []

    def visit(self, url):
        if self.back_stack and self.back_stack[-1] == url:
            return
        self.back_stack.append(url)
        self.forward_stack.clear()

    def go_back(self):
        if len(self.back_stack) <= 1:
            return None
        current = self.back_stack.pop()
        self.forward_stack.append(current)
        return self.back_stack[-1]

    def go_forward(self):
        if not self.forward_stack:
            return None
        url = self.forward_stack.pop()
        self.back_stack.append(url)
        return url

    def reset(self, url):
        self.back_stack = [url]
        self.forward_stack.clear()

class Listener:
    def __init__(self, command_handler, query_handler, reset_visited=False, auto_interval=0):
        self.cmd_handler = command_handler
        self.qry_handler = query_handler
        self.history = BrowserHistory()
        self.playwright = None
        self.browser = None
        self._stop_event = threading.Event()
        self.auto_interval = auto_interval
        self.msg_counter = 0  # счётчик для последовательной генерации сообщений

        if reset_visited:
            self.cmd_handler.repo.reset_all_visited()

        start_url = get_current_url()
        if start_url:
            self.history.reset(start_url)

    def _ensure_browser(self):
        if self.browser is None:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.connect_over_cdp('http://127.0.0.1:9222')

    def _send_message_bruteforce(self):
        """Генерирует сообщение по текущему счётчику, печатает и отправляет."""
        text = generate_message(self.msg_counter)
        self.msg_counter += 1
        time.sleep(0.2)
        keyboard.write(text, delay=0.02)
        keyboard.send('enter')
        print(f'Auto-sent: {text}', flush=True)

    def _on_save(self):
        try:
            url = get_current_url()
            if url:
                added = self.cmd_handler.handle(AddLinkCommand(url))
                if added:
                    print(f'Saved: {url}', flush=True)
                else:
                    print(f'Already in DB: {url}', flush=True)
            else:
                print('Could not get active tab URL', flush=True)
        except Exception as e:
            print(f'Error saving: {e}', flush=True)

    def _on_delete(self):
        try:
            url = get_current_url()
            if url:
                deleted = self.cmd_handler.handle(DeleteLinkCommand(url))
                if deleted:
                    print(f'Deleted: {url}', flush=True)
                else:
                    print(f'Not found: {url}', flush=True)
            else:
                print('Could not get active tab URL', flush=True)
        except Exception as e:
            print(f'Error deleting: {e}', flush=True)

    def _on_next(self):
        try:
            self._ensure_browser()
            next_url = self.qry_handler.handle(GetNextLinkQuery())
            if next_url:
                open_url(self.browser, next_url)
                self.history.visit(next_url)
                print(f'Next: {next_url}', flush=True)
            else:
                print('No more unvisited links', flush=True)
        except Exception as e:
            print(f'Error: {e}', flush=True)

    def _on_prev(self):
        try:
            self._ensure_browser()
            current_url = get_current_url()
            prev = self.history.go_back()
            if prev:
                if current_url:
                    self.cmd_handler.repo.set_visited(current_url, False)
                open_url(self.browser, prev)
                print(f'Back: {prev}', flush=True)
            else:
                print('No back history', flush=True)
        except Exception as e:
            print(f'Error: {e}', flush=True)

    def _on_forward(self):
        try:
            self._ensure_browser()
            current_url = get_current_url()
            fwd = self.history.go_forward()
            if fwd:
                if current_url:
                    self.cmd_handler.repo.set_visited(current_url, False)
                open_url(self.browser, fwd)
                print(f'Forward: {fwd}', flush=True)
            else:
                print('No forward history', flush=True)
        except Exception as e:
            print(f'Error: {e}', flush=True)

    def _print_url(self):
        try:
            url = get_current_url()
            print(f'Current URL: {url}', flush=True)
        except Exception as e:
            print(f'Error: {e}', flush=True)

    def _auto_loop(self):
        while not self._stop_event.is_set():
            self._on_next()                   # переходим на следующий чат
            if self._stop_event.is_set():
                return
            time.sleep(1.5)                   # ждём загрузку страницы и фокус поля
            self._send_message_bruteforce()   # отправляем сообщение с последовательной генерацией
            if self._stop_event.is_set():
                return
            time.sleep(self.auto_interval)    # пауза перед следующим чатом

    def start(self):
        keyboard.add_hotkey('insert', self._on_save)
        keyboard.add_hotkey('delete', self._on_delete)
        keyboard.add_hotkey('page up', self._on_next)
        keyboard.add_hotkey('page down', self._on_prev)
        keyboard.add_hotkey('home', self._print_url)
        keyboard.add_hotkey('f12', self._print_url)

        print("Hotkeys:", flush=True)
        print("  Insert    - Save current URL", flush=True)
        print("  Delete    - Delete current URL", flush=True)
        print("  Page Up   - Next unvisited link", flush=True)
        print("  Page Down - Back in history", flush=True)
        print("  Home/F12  - Show current URL", flush=True)
        if self.auto_interval > 0:
            print(f"  Auto-mode: switching every {self.auto_interval} sec with sequential unique messages", flush=True)
            threading.Thread(target=self._auto_loop, daemon=True).start()

        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=0.5)
        keyboard.unhook_all()

    def stop(self):
        self._stop_event.set()
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except:
                pass
        print("Listener stopped.", flush=True)

    def close(self):
        self.stop()
