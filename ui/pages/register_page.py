import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import database

DB_PATH = "schedule_manager.db"   # Database file name (must match database.py)

class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Layout container
        wrapper = ttk.Frame(self, padding=20)
        wrapper.pack(fill="both", expand=True)

        ttk.Label(wrapper, text="Create Account").pack(anchor="w", pady=(0,10))


        # Quick return to login (appears before the create/back buttons
        
        ttk.Button(
            wrapper,
            text = "Return to Login",
            command=lambda: self.controller.show_frame("LoginPage")
        ).pack(side="bottom", fill="x", pady=(12,0))

        # Username
        ttk.Label(wrapper, text="New Username").pack(anchor="w")
        self.user_var = tk.StringVar()
        self.user_entry = ttk.Entry(wrapper, textvariable=self.user_var, width=30)
        self.user_entry.pack(fill='x', pady=(4,10))
        
        # Password
        ttk.Label(wrapper, text="New Password").pack(anchor="w")
        self.pw_var = tk.StringVar()
        self.pw_entry = ttk.Entry(wrapper, textvariable=self.pw_var, show="•", width=30)
        self.pw_entry.pack(fill='x', pady=(4,10))

        # Confirm Password
        ttk.Label(wrapper, text="Confirm Password").pack(anchor="w")
        self.pw2_var = tk.StringVar()
        self.pw2_entry = ttk.Entry(wrapper, textvariable=self.pw2_var, show="•", width=30)
        self.pw2_entry.pack(fill='x', pady=(4,10))

        # Show Passwords toggle
        self.show_pw = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            wrapper, text="Show passwords", variable=self.show_pw, command=self._toggle_passwords
        ).pack(anchor="w")

        # Actions
        btns = ttk.Frame(wrapper)
        btns.pack(fill="x", pady=(12,0))
        ttk.Button(btns, text="Create Account", command=self._register).pack(side="right")
        ttk.Button(btns, text="Back to Login", 
                   command=lambda: self.controller.show_frame("LoginPage").pack(side="left"))
        
        self.user_entry.bind("<Return>", lambda _e: self._register())
        self.pw_entry.bind("<Return>", lambda _e: self._register())
        self.pw2_entry.bind("<Return>", lambda _e: self._register())

    def on_show(self):
        self.user_var.set("")
        self.pw_var.set("")
        self.pw2_var.set("")
        self.user_entry.focus_set()

    def _toggle_passwords(self):
        show = "" if self.show_pw.get() else "•"
        self.pw_entry.config(show=show)
        self.pw2_entry.config(show=show)

    def _register(self):
        username = self.user_var.get().strip()
        pw = self.pw_var.get()
        pw2 = self.pw_confirm_var.get()

        #basic validation
        if not username or not pw or not pw2:
            messagebox.showwarning("Missing Info", "All fields are required.")
            return
        if pw != pw2:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return
        if len(pw) < 8:
            messagebox.showerror("Weak Password", "Password must be at least 8 characters.")
            return
        
        # insert new user
        try:
            pwd_hash = database.hash_password(pw)
            with sqlite3.connect(DB_PATH) as conn:
                curr = conn.cursor()
                curr.exececute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, pwd_hash)
                )
                conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Failed", "Username already exists.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Could not create account: {e}")

        messagebox.showinfo("Success", "Account Created. You can now log in.")
        self.controller.show_frame("LoginPage")