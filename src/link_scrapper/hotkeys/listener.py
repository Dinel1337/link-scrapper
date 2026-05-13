import keyboard
import threading
import time
import queue
from link_scrapper.domain.commands import AddLinkCommand, DeleteLinkCommand
from link_scrapper.queries.link_queries import GetNextLinkQuery
from link_scrapper.services.browser import get_current_url, open_url
from link_scrapper.services.templates import generate_message, MESSAGE_CLASSES
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
    def __init__(self, command_handler, query_handler, reset_visited=False, auto_interval=0, skip=0, count=0):
        self.cmd_handler = command_handler
        self.qry_handler = query_handler
        self.history = BrowserHistory()
        self.playwright = None
        self.browser = None
        self._stop_event = threading.Event()
        self.auto_interval = auto_interval
        self.msg_counter = 0
        self.cmd_queue = queue.Queue()
        self._auto_timer = None
        self._auto_state = None
        self.chats_processed = 0
        self.max_chats = count          # 0 = без ограничений

        if reset_visited:
            self.cmd_handler.repo.reset_all_visited()

        for _ in range(skip):
            if self.qry_handler.handle(GetNextLinkQuery()) is None:
                break

        start_url = get_current_url()
        if start_url:
            self.history.reset(start_url)

    def _ensure_browser(self):
        try:
            self.browser.close()
        except:
            pass
        try:
            self.playwright.stop()
        except:
            pass
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp('http://127.0.0.1:9222')

    def _send_message(self, index: int):
        text = generate_message(index)
        keyboard.write(text, delay=0.02)
        keyboard.send('enter')
        print(f'Auto-sent [{index+1}/7]: {text}', flush=True)

    # ---------- неблокирующий авто‑шаг ----------
    def _start_auto_step(self):
        if self._auto_state is None:
            self._auto_state = {'stage': 'open', 'msg_i': 0}

        state = self._auto_state

        if state['stage'] == 'open':
            try:
                self._ensure_browser()
            except Exception as e:
                print(f'Browser reconnect failed: {e}', flush=True)
                self._schedule_next_auto()
                self._auto_state = None
                return True

            next_url = self.qry_handler.handle(GetNextLinkQuery())
            if not next_url:
                print('No more unvisited links', flush=True)
                self._auto_state = None
                return True

            try:
                open_url(self.browser, next_url)
            except Exception as e:
                print(f'Error opening URL, skipping: {next_url}', flush=True)
                self._schedule_next_auto()
                self._auto_state = None
                return True

            self.history.visit(next_url)
            print(f'Next: {next_url}', flush=True)
            state['stage'] = 'wait_load'
            state['wait_start'] = time.time()
            return False

        elif state['stage'] == 'wait_load':
            if time.time() - state['wait_start'] < 2.0:
                return False
            state['stage'] = 'messages'
            state['msg_i'] = 0
            return False

        elif state['stage'] == 'messages':
            if state['msg_i'] >= 7 or self._stop_event.is_set():
                print(f'--- Finished chat, waiting {self.auto_interval}s ---', flush=True)
                self.chats_processed += 1
                # проверка лимита
                if self.max_chats > 0 and self.chats_processed >= self.max_chats:
                    print(f'Reached limit of {self.max_chats} chats. Auto-mode stopped.', flush=True)
                    self._auto_state = None
                    return True   # завершаем, больше не планируем
                self._schedule_next_auto()
                self._auto_state = None
                return True
            try:
                self._send_message(self.msg_counter)
                self.msg_counter += 1
                state['msg_i'] += 1
            except Exception as e:
                print(f'Send message failed: {e}', flush=True)
                self._schedule_next_auto()
                self._auto_state = None
                return True
            state['stage'] = 'wait_msg'
            state['wait_start'] = time.time()
            return False

        elif state['stage'] == 'wait_msg':
            if time.time() - state['wait_start'] < 0.3:
                return False
            state['stage'] = 'messages'
            return False

        return False

    def _schedule_next_auto(self):
        if self._stop_event.is_set():
            return
        if self._auto_timer:
            self._auto_timer.cancel()
        self._auto_timer = threading.Timer(
            self.auto_interval,
            lambda: self.cmd_queue.put('auto_step')
        )
        self._auto_timer.daemon = True
        self._auto_timer.start()

    # ---------- ручные команды ----------
    def _do_save(self):
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

    def _do_delete(self):
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

    def _do_next(self):
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

    def _do_prev(self):
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

    def _do_forward(self):
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

    def _do_print_url(self):
        try:
            url = get_current_url()
            print(f'Current URL: {url}', flush=True)
        except Exception as e:
            print(f'Error: {e}', flush=True)

    # ---------- колбэки клавиш ----------
    def _on_save(self):
        self.cmd_queue.put('save')
    def _on_delete(self):
        self.cmd_queue.put('delete')
    def _on_next(self):
        self.cmd_queue.put('next')
    def _on_prev(self):
        self.cmd_queue.put('prev')
    def _on_forward(self):
        self.cmd_queue.put('forward')
    def _print_url(self):
        self.cmd_queue.put('print_url')

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
            limit_str = f", limit: {self.max_chats} chats" if self.max_chats > 0 else ""
            print(f"  Auto-mode: 7 messages per chat, interval: {self.auto_interval}s{limit_str}", flush=True)
            self.cmd_queue.put('auto_step')

        while not self._stop_event.is_set():
            try:
                while True:
                    cmd = self.cmd_queue.get_nowait()
                    if cmd == 'save':
                        self._do_save()
                    elif cmd == 'delete':
                        self._do_delete()
                    elif cmd == 'next':
                        self._do_next()
                    elif cmd == 'prev':
                        self._do_prev()
                    elif cmd == 'forward':
                        self._do_forward()
                    elif cmd == 'print_url':
                        self._do_print_url()
                    elif cmd == 'auto_step':
                        self._start_auto_step()
            except queue.Empty:
                pass

            if self._auto_state is not None:
                finished = self._start_auto_step()
                if finished:
                    self._auto_state = None

            time.sleep(0.05)

        keyboard.unhook_all()

    def stop(self):
        self._stop_event.set()
        if self._auto_timer:
            self._auto_timer.cancel()
        try:
            self.browser.close()
        except:
            pass
        try:
            self.playwright.stop()
        except:
            pass
        print("Listener stopped.", flush=True)

    def close(self):
        self.stop()
