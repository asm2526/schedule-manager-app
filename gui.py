# gui.py
# ------------------------------------
# This file creates a simple GUI login and registration system
# for your schedule manager project.
# It uses Tkinter (Python's built-in GUI toolkit)
# and your existing database.py for user storage/verification.
# ------------------------------------

import tkinter as tk              # GUI library
from tkinter import messagebox    # Popup dialogs for errors/info
import sqlite3                    # To interact with SQLite for registration
import database                   # Your own database.py file with hashing + verify_user

DB_PATH = "schedule_manager.db"   # Database file name (must match database.py)




# -------------------------------------------------------------------
# Helper function for registering new users (CREATE ACCOUNT)
# -------------------------------------------------------------------
def create_user(username: str, password: str) -> bool:
    """
    Try to create a new user in the SQLite DB.
    Returns True if successful, False if username already exists.
    """
    if not username or not password:
        return False  # Basic validation: no empty usernames/passwords
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Use the same hashing function from database.py
        pwd_hash = database.hash_password(password)

        # Insert user into DB, with UNIQUE constraint on username
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, pwd_hash)
        )

        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        # This exception is raised if username already exists (unique constraint)
        return False

# -------------------------------------------------------------------
# Main Login Window
# -------------------------------------------------------------------
class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()  # Initialize the Tk root window

        # --- Window setup ---
        self.title("Schedule Manager - Login")  # Title of the window
        self.geometry("360x220")                # Fixed size
        self.resizable(False, False)            # Prevent resize

        # Ensure database and "tester" sample user exist
        database.init_db()

        # --- Username input ---
        tk.Label(self, text="Username").pack(pady=(16, 4))
        self.username_var = tk.StringVar()   # String holder
        self.username_entry = tk.Entry(self, textvariable=self.username_var)
        self.username_entry.pack()

        # --- Password input ---
        tk.Label(self, text="Password").pack(pady=(10, 4))
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(self, textvariable=self.password_var, show="•")
        # "show" replaces typed characters with • to mask password
        self.password_entry.pack()

        # --- Checkbox to show/hide password ---
        self.show_pw = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self, text="Show password", variable=self.show_pw,
            command=self.toggle_password
        ).pack(pady=(6, 0))

        # --- Buttons for Login & Register ---
        btn_frame = tk.Frame(self)  # Horizontal frame for buttons
        btn_frame.pack(pady=14)

        tk.Button(btn_frame, text="Login", width=12, command=self.do_login).grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Register", width=12, command=self.open_register).grid(row=0, column=1, padx=6)

        # --- Bind Enter key to login for convenience ---
        self.bind("<Return>", lambda _e: self.do_login())

        # Focus cursor in username field on startup
        self.username_entry.focus_set()

    # Toggle password visibility
    def toggle_password(self):
        self.password_entry.config(show="" if self.show_pw.get() else "•")

    # Login button action
    def do_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        # Ensure fields are filled
        if not username or not password:
            messagebox.showwarning("Missing info", "Please enter both username and password.")
            return

        # Check credentials against database
        try:
            ok = database.verify_user(username, password)
        except Exception as e:
            messagebox.showerror("Error", f"Login failed due to an error:\n{e}")
            return

        if ok:
            self.open_main_app(username)  # Open next window on success
        else:
            messagebox.showerror("Login failed", "Invalid username or password.")

    # Register button action
    def open_register(self):
        RegisterDialog(self)

    # Dummy "main app" window that opens after login
    def open_main_app(self, username: str):
        top = tk.Toplevel(self)  # New window
        top.title("Schedule Manager")
        top.geometry("500x320")

        # Placeholder content
        tk.Label(top, text=f"Welcome, {username}!", font=("Arial", 14)).pack(pady=20)
        tk.Label(top, text="(Build your schedule manager UI here)").pack(pady=6)
        tk.Button(top, text="Log out", command=top.destroy).pack(pady=20)

# -------------------------------------------------------------------
# Registration Dialog (pops up when user clicks "Register")
# -------------------------------------------------------------------
class RegisterDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)  # Child window

        # --- Window setup ---
        self.title("Register New User")
        self.geometry("360x240")
        self.resizable(False, False)

        # Keep dialog in focus above parent
        self.transient(parent)
        self.grab_set()

        # --- Username ---
        tk.Label(self, text="New Username").pack(pady=(14, 4))
        self.user_var = tk.StringVar()
        tk.Entry(self, textvariable=self.user_var).pack()

        # --- Password ---
        tk.Label(self, text="Password").pack(pady=(10, 4))
        self.pw_var = tk.StringVar()
        self.pw_entry = tk.Entry(self, textvariable=self.pw_var, show="•")
        self.pw_entry.pack()

        # --- Confirm Password ---
        tk.Label(self, text="Confirm Password").pack(pady=(10, 4))
        self.pw2_var = tk.StringVar()
        self.pw2_entry = tk.Entry(self, textvariable=self.pw2_var, show="•")
        self.pw2_entry.pack()

        # --- Checkbox show/hide both passwords ---
        self.show_pw = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self, text="Show passwords", variable=self.show_pw,
            command=self.toggle_passwords
        ).pack(pady=(6, 0))

        # --- Button to confirm registration ---
        tk.Button(self, text="Create Account", command=self.register).pack(pady=12)

        # Enter key submits registration
        self.bind("<Return>", lambda _e: self.register())

        # Focus cursor in password field
        self.pw_entry.focus_set()

    def toggle_passwords(self):
        # Toggle masking for both password fields
        show = "" if self.show_pw.get() else "•"
        self.pw_entry.config(show=show)
        self.pw2_entry.config(show=show)

    def register(self):
        # Grab values
        username = self.user_var.get().strip()
        pw = self.pw_var.get()
        pw2 = self.pw2_var.get()

        # Basic checks
        if not username or not pw or not pw2:
            messagebox.showwarning("Missing info", "All fields are required.")
            return
        if pw != pw2:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return
        if len(pw) < 8:
            messagebox.showwarning("Weak password", "Use at least 8 characters.")
            return

        # Try creating user in DB
        ok = create_user(username, pw)
        if ok:
            messagebox.showinfo("Success", "Account created. You can now log in.")
            self.destroy()
        else:
            messagebox.showerror("Failed", "Username already exists or invalid data.")

# -------------------------------------------------------------------
# MAIN PROGRAM ENTRY
# -------------------------------------------------------------------
if __name__ == "__main__":
    try:
        app = LoginApp()
        app.mainloop()
    except Exception as e:
        import traceback, sys
        traceback.print_exc()  # shows full stack in terminal
        try:
            from tkinter import messagebox, Tk
            root = Tk(); root.withdraw()
            messagebox.showerror("Startup error", f"{e}\n\nSee terminal for details.")
            root.destroy()
        except Exception:
            # If Tk can't even start, at least exit non-zero
            sys.exit(1)

