from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
import database

class LoginPage(QWidget):
    """Login screen for existing users"""

    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        #Title
        title = QLabel("Login Page")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        #username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        # password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password) #hide text
        layout.addWidget(self.password_input)

        # new: show password checkbox
        self.show_password_cb = QCheckBox("Show Password")
        self.show_password_cb.toggled.connect(self.toggle_password)
        layout.addWidget(self.show_password_cb)

        #Login button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        #Register btn
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(lambda: self.app.show_page("RegisterPage"))
        layout.addWidget(register_btn)

        self.setLayout(layout)

        # Bind enter key to trigger login
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        login_btn.setDefault(True)

    def toggle_password(self, checked: bool):
        """Toggle between showing and hiding the password field"""
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def handle_login(self):
        """Validate login credentials"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Missing Info", "Please enter both username and password.")
            return
        
        try:
            if database.verify_user(username, password):
                self.app.current_user = username
                QMessageBox.information(self, "Login Successs", f"Welcome, {username}!")
                self.app.show_page("CalendarPage")
            else:
                QMessageBox.critical(self, "Login Failed", "Invalid username or password")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login Failed: {e}")