import tkinter as tk
from tkinter import ttk, messagebox

#keep using existing root-level database.py for now
import schedule_manager_app.database as database

# styles 
try:
    from .ui.styles import apply_style
except Exception:
    def apply_style(_): pass

# pages: support BOTH new package and current root locations
try:
    from .ui.pages.login_page import LoginPage
    from .ui.pages.register_page import RegisterPage
    from .ui.pages.home_page import HomePage
    from .ui.pages.today_page import TodayPage
    from .ui.pages.calendar_page import CalendarPage 
except Exception:
    from ui.pages.login_page import LoginPage
    from ui.pages.register_page import RegisterPage
    from ui.pages.home_page import HomePage
    from ui.pages.today_page import TodayPage
    from ui.pages.calendar_page import CalendarPage



APP_TITLE = "Schedule Manager"
START_SIZE = (900,600)
MIN_SIZE = (640,420)
class App(tk.Tk):
    """Main application window and page router"""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
       
        #enabling resizing + setting initial and minimum size
        self.geometry(f"{START_SIZE[0]}x{START_SIZE[1]}")
        self.minsize(*MIN_SIZE)
        self.resizable(True, True)

        #improve DPI scaling aon HiDPI screens
        try:
            self.tk.call("tk", "scaling", 1.25)
        except Exception:
            pass
        #global ttk styles
        apply_style(ttk.Style(self))

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
        for Page in (LoginPage, RegisterPage, HomePage, TodayPage, CalendarPage):
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
