from tkinter import ttk

class CalendarPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        wrapper = ttk.Frame(self, padding=20)
        wrapper.pack(fill="both", expand=True)

        ttk.Label(wrapper, text="Calendar View (Placeholder)").pack(anchor="w", pady=(0, 10))
        ttk.Label(wrapper, text="(Calendar functionality to be implemented)").pack(anchor="w", pady=(6, 12))

        ttk.Button(wrapper,
                   text="Back",
                   command=lambda: self.controller.show_frame("HomePage")).pack(anchor="e", pady=(8,0))