import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class TodayPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        wrapper = ttk.Frame(self, padding=20)
        wrapper.pack(fill="both", expand=True)

        today_str = datetime.now().strftime("%A, %B %d, %Y")
        ttk.Label(wrapper, text=f"Today's Appointments — {today_str}").pack(anchor="w", pady=(0, 10))

        # placeholder content (will look at db later)
        self._empty = ttk.Label(wrapper, text="No appointments scheduled for today.")
        self._empty.pack(anchor="w", pady=(6, 12))

        # back
        ttk.Button(wrapper,
                    text="Back to Home",
                    command=lambda: self.controller.show_frame("HomePage")
                    ).pack(anchor="e", pady=(8,0))
        



