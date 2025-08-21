import tkinter as tk
from tkinter import ttk, messagebox
import database

from ui.pages.login_page import LoginPage
from ui.pages.register_page import RegisterPage
from ui.pages.home_page import HomePage

APP_TITLE = "Schedule Manager"
WINDOW_SIZE = "500x320"

class App(tk.Tk):
    """Main application window and page router"""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)

        # Ensure DB is ready
        try:
            database.init_db()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize the database:\n{e}")

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.current_user = None
        self.frames = {}

        # Register each page class here
        for Page in (LoginPage, RegisterPage, HomePage):
            name = Page.__name__
            frame = Page(parent=container, controller=self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Start on login
        self.show_frame("LoginPage")

    # ---------- Navigation helpers ----------
    def show_frame(self, name: str) -> None:
        """Raise the page with the given class name"""
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            try:
                frame.on_show()
            except Exception:
                pass

    def set_user(self, username: str | None) -> None:
        """Set/clear the logged-in user for session state"""
        self.current_user = username


if __name__ == "__main__":
    app = App()
    app.mainloop()
