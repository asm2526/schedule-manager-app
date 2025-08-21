import tkinter as tk
from tkinter import ttk, messagebox

import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# .../ui/pages/login_page.py -> parents: pages (1), ui (2), project root (3)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import database

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        #layout container
        wrapper = ttk.Frame(self, padding=20)
        wrapper.pack(fill="both", expand=True)

        ttk.Label(wrapper, text="Sign in").pack(anchor="w", pady=(0, 10))

        # Username input
        ttk.Label(wrapper, text="Username").pack(anchor="w")
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(wrapper, textvariable=self.username_var, width=30)
        self.username_entry.pack(fill="x", pady=(4, 10))

        # Password input
        ttk.Label(wrapper, text="Password").pack(anchor="w")
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(wrapper, textvariable=self.password_var, show="•", width=30)
        self. password_entry.pack(fill="x", pady=(4, 10))

        # Show password toggle
        self.show_pw = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            wrapper, text="Show password", variable=self.show_pw, command=self._toggle_password
        ).pack(anchor="w")

        #Buttons row
        btns = ttk.Frame(wrapper)
        btns.pack(fill="x", pady=(12, 0))

        ttk.Button(btns, text="Login", command=self._do_login).pack(side="left")
        ttk.Button(btns, text="Register", command=lambda: self.controller.show_frame("RegisterPage")
                   ).pack(side="right")
        
        # Enter submits login from either field
        self.username_entry.bind("<Return>", lambda _e: self._do_login())
        self.password_entry.bind("<Return>", lambda _e: self._do_login())

    # called by app after page is raise
    def on_show(self):
        self.username_entry.focus_set()  # Focus on username field when shown

    def _toggle_password(self):
        self.password_entry.config(show="" if self.show_pw.get() else "•")

    def _do_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showwarning("Missing Info", "Please enter both username and password.")
            return
        
        try:
            ok = database.verify_user(username, password)
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {e}")
            return
        
        if ok:
            # save session user and move to HomePage
            self.controller.set_user(username)
            home = self.controller.frames.get("HomePage")
            if home and hasattr(home, "set_welcome"):
                home.set_welcome(username)
            self.controller.show_frame("HomePage")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
        

