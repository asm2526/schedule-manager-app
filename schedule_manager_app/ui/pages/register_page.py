# ui/pages/register_page.py

import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure we can import the root-level database.py from ui/pages/
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import database  # still uses sqlite3 under the hood


class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Layout container
        wrapper = ttk.Frame(self, padding=20)
        wrapper.pack(fill="both", expand=True)

        ttk.Label(wrapper, text="Create Account").pack(anchor="w", pady=(0, 10))

        # --- Username ---
        ttk.Label(wrapper, text="New Username").pack(anchor="w")
        self.user_var = tk.StringVar()
        self.user_entry = ttk.Entry(wrapper, textvariable=self.user_var, width=30)
        self.user_entry.pack(fill="x", pady=(4, 10))

        # --- Password ---
        ttk.Label(wrapper, text="New Password").pack(anchor="w")
        self.pw_var = tk.StringVar()
        self.pw_entry = ttk.Entry(wrapper, textvariable=self.pw_var, show="•", width=30)
        self.pw_entry.pack(fill="x", pady=(4, 10))

        # --- Confirm Password ---
        ttk.Label(wrapper, text="Confirm Password").pack(anchor="w")
        self.pw2_var = tk.StringVar()
        self.pw2_entry = ttk.Entry(wrapper, textvariable=self.pw2_var, show="•", width=30)
        self.pw2_entry.pack(fill="x", pady=(4, 10))

        # Show Passwords toggle
        self.show_pw = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            wrapper,
            text="Show passwords",
            variable=self.show_pw,
            command=self._toggle_passwords,
        ).pack(anchor="w")

        # --- Actions row ---
        btns = ttk.Frame(wrapper)
        btns.pack(fill="x", pady=(12, 0))

        ttk.Button(
            btns,
            text="Create Account",
            command=self._register,   # FIX: calls our register method
        ).pack(side="right")

        footer = ttk.Frame(wrapper)
        footer.pack(side="bottom", fill="x", pady=(12, 0))
        ttk.Button(
            footer,
            text="Already have an account? Log in",
            command=lambda: self.controller.show_frame("LoginPage"),
        ).pack(side="left", anchor="center")

        # Enter submits
        for w in (self.user_entry, self.pw_entry, self.pw2_entry):
            w.bind("<Return>", lambda _e: self._register())

    def on_show(self):
        self.user_var.set("")
        self.pw_var.set("")
        self.pw2_var.set("")
        self.show_pw.set(False)
        self._toggle_passwords()
        self.user_entry.focus_set()

    def _toggle_passwords(self):
        show = "" if self.show_pw.get() else "•"
        self.pw_entry.config(show=show)
        self.pw2_entry.config(show=show)

    def _register(self):
        username = self.user_var.get().strip()
        pw = self.pw_var.get()
        pw2 = self.pw2_var.get()   # FIX: use the correct confirm var

        # Basic validation
        if not username or not pw or not pw2:
            messagebox.showwarning("Missing Info", "All fields are required.")
            return
        if pw != pw2:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return
        if len(pw) < 8:
            messagebox.showerror("Weak Password", "Password must be at least 8 characters.")
            return

        # Prefer centralized helper so Register/Login share the SAME SQLite DB file
        ok: bool
        if hasattr(database, "create_user"):
            ok = database.create_user(username, pw)
        else:
            # Fallback: direct sqlite3 insert using database.DB_FILE if available
            db_path = getattr(database, "DB_FILE", os.path.join(ROOT, "schedule_manager.db"))
            try:
                with sqlite3.connect(db_path) as conn:
                    conn.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username, database.hash_password(pw)),
                    )  
                    conn.commit()
                ok = True
            except sqlite3.IntegrityError:
                ok = False
            except Exception as e:
                messagebox.showerror("Error", f"Could not create account: {e}")
                return

        if not ok:
            messagebox.showerror("Failed", "Username already exists.")
            return

        messagebox.showinfo("Success", "Account created. You can now log in.")
        self.controller.show_frame("LoginPage")
