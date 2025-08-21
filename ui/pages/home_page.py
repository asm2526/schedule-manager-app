# pages/home_page.py — post-login placeholder (minimal, no styling)
from tkinter import ttk

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Layout container
        wrapper = ttk.Frame(self, padding=20)
        wrapper.pack(fill="both", expand=True)

        # Welcome header (updated after successful login)
        self._welcome = ttk.Label(wrapper, text="Welcome!")
        self._welcome.pack(anchor="w")

        # Placeholder content area
        ttk.Label(
            wrapper,
            text="(Your schedule manager UI will go here.)"
        ).pack(anchor="w", pady=(6, 14))

        # Logout
        ttk.Button(wrapper, text="Log out", command=self._logout).pack(anchor="e")

    def set_welcome(self, username: str):
        """Called by LoginPage after successful login."""
        self._welcome.configure(text=f"Welcome, {username}!")

    def on_show(self):
        """Optional hook if you need to refresh data when page is shown."""
        pass

    def _logout(self):
        self.controller.set_user(None)
        self.controller.show_frame("LoginPage")
