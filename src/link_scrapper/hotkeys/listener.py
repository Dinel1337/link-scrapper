import keyboard
from link_scrapper.domain.commands import AddLinkCommand, DeleteLinkCommand
from link_scrapper.queries.link_queries import GetNextLinkQuery
from link_scrapper.services.browser import get_current_url, open_url

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
    def __init__(self, command_handler, query_handler):
        self.cmd_handler = command_handler
        self.qry_handler = query_handler
        self.history = BrowserHistory()
        start_url = get_current_url()
        if start_url:
            self.history.reset(start_url)

    def _on_save(self):
        try:
            url = get_current_url()
            if url:
                added = self.cmd_handler.handle(AddLinkCommand(url))
                if added:
                    print(f'Saved: {url}')
                else:
                    print(f'Already in DB: {url}')
            else:
                print('Could not get active tab URL')
        except Exception as e:
            print(f'Error saving: {e}')

    def _on_delete(self):
        try:
            url = get_current_url()
            if url:
                deleted = self.cmd_handler.handle(DeleteLinkCommand(url))
                if deleted:
                    print(f'Deleted: {url}')
                else:
                    print(f'Not found: {url}')
            else:
                print('Could not get active tab URL')
        except Exception as e:
            print(f'Error deleting: {e}')

    def _on_next(self):
        try:
            next_url = self.qry_handler.handle(GetNextLinkQuery())
            if next_url:
                open_url(next_url)
                self.history.visit(next_url)
                print(f'Next: {next_url}')
            else:
                print('No more unvisited links')
        except Exception as e:
            print(f'Error: {e}')

    def _on_prev(self):
        try:
            prev = self.history.go_back()
            if prev:
                open_url(prev)
                print(f'Back: {prev}')
            else:
                print('No back history')
        except Exception as e:
            print(f'Error: {e}')

    def _print_url(self):
        try:
            url = get_current_url()
            print(f'Current URL: {url}')
        except Exception as e:
            print(f'Error: {e}')
    
    def start(self):
        keyboard.add_hotkey('grave', self._on_save)
        keyboard.add_hotkey('.', self._on_next)
        keyboard.add_hotkey(',', self._on_prev)
        keyboard.add_hotkey('f2', self._on_delete)
        keyboard.add_hotkey('f12', self._print_url)
        print("Hotkeys:  save | . next | , back | F2 delete | F12 print URL | Ctrl+C to exit")
        keyboard.wait()
