from tkinter import ttk, messagebox

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

        ttk.Label(wrapper, text="What would you like to do today?").pack(anchor="w", pady=(6,10))

        """New navigation buttons"""

        nav = ttk.Frame(wrapper)
        nav.pack(fill="x", pady=(16,4))

        ttk.Button(
            nav,
            text="Today's Schedule",
            command=lambda: self.controller.show_frame("TodayPage")
        ).pack(fill="x", pady=(6,0))

        ttk.Button(
            nav,
            text="View Calendar",
            command=lambda: self.controller.show_frame("CalendarPage")
        ).pack(fill="x")

        # Logout button
        ttk.Button(
            wrapper,
            text="Log out",
            command=lambda: (self.controller.set_user(None), self.controller.show_frame("LoginPage"))
        ).pack(side="bottom", fill="x", pady=(12,0))
        
    def set_welcome(self, username: str) -> None:
        self._welcome.configure(text=f"Welcome, {username}!")

    def on_show(self):
        pass  # Placeholder for any actions when this page is shown


    '''def _logout(self):
        print("[Homepage] Loggin out...")
        try:
            self.controller.set_user(None)
            self.controller.show_frame("LoginPage")
            print("[Homepage] navigated to loginpage")
        except Exception as e:
            messagebox.showerror("Error", f"Logout failed: {e}")
            '''
    
    #come back to logout helper function later it is better coding practice to have a logout helper function
    #but for now it is not needed as the logout button is working fine