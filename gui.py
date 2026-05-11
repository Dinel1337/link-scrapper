import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import subprocess
import sys
import queue
from PIL import Image, ImageDraw, ImageTk

from link_scrapper.container import create_app

# ---------- палитра ----------
BG_GRADIENT_TOP = "#1a1a2e"
BG_GRADIENT_BOTTOM = "#16213e"
ACCENT = "#0f3460"
BUTTON_START = "#00b4d8"
BUTTON_RESUME = "#0096c7"
BUTTON_STOP = "#e63946"
BUTTON_CLEAR = "#f4a261"
TEXT_LIGHT = "#f1faee"
SUCCESS_GREEN = "#2ecc71"
STOP_RED = "#e74c3c"

# ---------- градиентный фон ----------
def create_gradient_bg(width, height, top_color, bottom_color):
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    r1, g1, b1 = [int(top_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    r2, g2, b2 = [int(bottom_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    for y in range(height):
        ratio = y / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return ImageTk.PhotoImage(img)

# ---------- кнопка ----------
class HoverButton(tk.Label):
    def __init__(self, parent, text, icon="", command=None,
                 bg_normal="#00b4d8", bg_hover="#0096c7", fg=TEXT_LIGHT,
                 font=("Segoe UI", 11, "bold"), width_char=28, **kwargs):
        display = f"{icon}  {text}" if icon else text
        super().__init__(parent, text=display,
                         bg=bg_normal, fg=fg, font=font,
                         relief="flat", bd=0,
                         width=width_char,
                         padx=10, pady=10,
                         cursor="hand2", anchor="center", **kwargs)
        self.bg_normal = bg_normal
        self.bg_hover = bg_hover
        self.command = command
        self.bind("<Enter>", lambda e: self.config(bg=self.bg_hover))
        self.bind("<Leave>", lambda e: self.config(bg=self.bg_normal))
        self.bind("<Button-1>", lambda e: self._click())

    def _click(self):
        if self.command:
            self.command()

# ---------- перенаправление вывода в текстовое поле ----------
class LogRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.running = True
        self.start()

    def write(self, string):
        if string:
            self.queue.put(string)

    def flush(self):
        pass

    def poll(self):
        while not self.queue.empty():
            msg = self.queue.get_nowait()
            self.text_widget.insert(tk.END, msg)
            self.text_widget.see(tk.END)
        if self.running:
            self.text_widget.after(100, self.poll)

    def start(self):
        self.poll()

    def stop(self):
        self.running = False

# ---------- главное окно ----------
class LinkScrapperGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Link Scrapper")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_GRADIENT_TOP)

        win_width = 420
        win_height = 550

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (win_width // 2)
        y = (screen_height // 2) - (win_height // 2)
        self.root.geometry(f"{win_width}x{win_height}+{x}+{y}")

        # градиентный фон
        self.bg_image = create_gradient_bg(win_width, win_height, BG_GRADIENT_TOP, BG_GRADIENT_BOTTOM)
        self.bg_label = tk.Label(self.root, image=self.bg_image, bd=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # заголовок
        title_frame = tk.Frame(self.root, bg=BG_GRADIENT_TOP, bd=0)
        title_frame.pack(pady=(15, 5))
        tk.Label(title_frame, text="🚀  Link Scrapper", fg=TEXT_LIGHT, bg=BG_GRADIENT_TOP,
                 font=("Segoe UI", 16, "bold")).pack()

        # статус
        self.status_frame = tk.Frame(self.root, bg=BG_GRADIENT_TOP)
        self.status_frame.pack(pady=(0, 10))
        self.status_dot = tk.Label(self.status_frame, text="●", font=("Arial", 14),
                                   fg=STOP_RED, bg=BG_GRADIENT_TOP)
        self.status_dot.pack(side=tk.LEFT, padx=(0, 8))
        self.status_label = tk.Label(self.status_frame, text="Stopped", fg=TEXT_LIGHT,
                                     bg=BG_GRADIENT_TOP, font=("Segoe UI", 10))
        self.status_label.pack(side=tk.LEFT)

        # кнопки
        btn_frame = tk.Frame(self.root, bg=BG_GRADIENT_TOP)
        btn_frame.pack(pady=10)

        self.btn_start = HoverButton(btn_frame, "Start (new session)", "▶️",
                                     command=self.start_new,
                                     bg_normal=BUTTON_START, bg_hover="#0077b6")
        self.btn_start.pack(pady=4)

        self.btn_resume = HoverButton(btn_frame, "Resume (continue)", "⏯️",
                                      command=self.start_resume,
                                      bg_normal=BUTTON_RESUME, bg_hover="#005f8c")
        self.btn_resume.pack(pady=4)

        self.btn_stop = HoverButton(btn_frame, "Stop", "⏹️",
                                    command=self.stop,
                                    bg_normal=BUTTON_STOP, bg_hover="#c1121f")
        self.btn_stop.pack(pady=4)

        self.btn_clear = HoverButton(btn_frame, "Clear DB", "🗑️",
                                     command=self.clear_db,
                                     bg_normal=BUTTON_CLEAR, bg_hover="#e76f51")
        self.btn_clear.pack(pady=4)

        # лог-панель
        self.log_area = scrolledtext.ScrolledText(
            self.root,
            height=12,
            width=46,
            bg="#0a0a1a",
            fg=TEXT_LIGHT,
            font=("Consolas", 9),
            insertbackground="white",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.log_area.pack(pady=(10, 5), padx=15, fill=tk.BOTH, expand=False)
        self.log_area.configure(state="normal")

        self.listener = None
        self.thread = None
        self.redirector = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _run_app(self, reset_visited):
        # Перенаправляем вывод в лог‑панель
        self.redirector = LogRedirector(self.log_area)
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = self.redirector
        sys.stderr = self.redirector

        try:
            app = create_app(reset_visited=reset_visited)
            self.listener = app
            self.update_status(True)
            app.start()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            if self.redirector:
                self.redirector.stop()
                self.redirector = None
            self.update_status(False)
            self.listener = None

    def start_new(self):
        if self.listener:
            messagebox.showwarning("Already running", "Stop first.")
            return
        subprocess.Popen(["cmd", "/c", "start", "msedge", "--remote-debugging-port=9222"], shell=True)
        self.thread = threading.Thread(target=self._run_app, args=(True,), daemon=True)
        self.thread.start()

    def start_resume(self):
        if self.listener:
            messagebox.showwarning("Already running", "Stop first.")
            return
        subprocess.Popen(["cmd", "/c", "start", "msedge", "--remote-debugging-port=9222"], shell=True)
        self.thread = threading.Thread(target=self._run_app, args=(False,), daemon=True)
        self.thread.start()

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.update_status(False)

    def clear_db(self):
        if messagebox.askyesno("Confirm", "Delete ALL saved links?"):
            from link_scrapper.infra.db import SessionLocal
            from link_scrapper.infra.repositories import LinkCommandRepository
            session = SessionLocal()
            repo = LinkCommandRepository(session)
            repo.delete_all()
            session.close()
            messagebox.showinfo("Done", "Database cleared.")

    def update_status(self, running: bool):
        color = SUCCESS_GREEN if running else STOP_RED
        text = "Running..." if running else "Stopped"
        self.status_dot.config(fg=color)
        self.status_label.config(text=text)

    def on_close(self):
        self.stop()
        self.root.destroy()

if __name__ == "__main__":
    LinkScrapperGUI().root.mainloop()