from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
import database

class RegisterPage(QWidget):
    """Registration screen for new users."""

    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        #Title
        title = QLabel("Register New Account")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        #username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        layout.addWidget(self.username_input)

        #password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        #password confirmation
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)

        # new: show password checkbox
        self.show_password_cb = QCheckBox("Show Passwords")
        self.show_password_cb.toggled.connect(self.toggle_passwords)
        layout.addWidget(self.show_password_cb)

        #Register button
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.handle_register)
        layout.addWidget(register_btn)

        # Back to login button
        back_btn = QPushButton("Back to Login")
        back_btn.clicked.connect(lambda: self.app.show_page("LoginPage"))
        layout.addWidget(back_btn)

        self.setLayout(layout)

        # Bind Enter key to trigger registration
        self.username_input.returnPressed.connect(self.handle_register)
        self.password_input.returnPressed.connect(self.handle_register)
        self.confirm_input.returnPressed.connect(self.handle_register)     
        register_btn.setDefault(True)

    def toggle_passwords(self, checked: bool):
        """Toggle between showing and hiding both password fields"""
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.password_input.setEchoMode(mode)
        self.confirm_input.setEchoMode(mode)

    def handle_register(self):
        """Attempt to register a new user."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not username or not password or not confirm:
            QMessageBox.warning(self, "Missing Info", "All fields are required")
            return

        if password != confirm:
            QMessageBox.warning(self, "Mismatch", "Passwords do not match.")
            return

        try:
            if database.create_user(username, password):
                QMessageBox.information(self, "Success", "Account Created!")
                self.app.show_page("LoginPage")
            else:
                QMessageBox.critical(self, "Error", "Username already exists.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {e}")

                 