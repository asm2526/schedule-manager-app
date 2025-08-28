from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)

import database

class LoginPage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        #Title
        layout.addWidget(QLabel("Login Page"))

        #Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password) #hide text
        layout.addWidget(self.password_input)

        #Login Button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        #Register Button
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(lambda: self.app.show_page("RegisterPage"))
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Missing Info", "Please enter both username and password.")
            return
        try:
            if database.verify_user(username, password):
                QMessageBox.information(self, "Login Success", f"Welcome, {username}!")
                # Navigate to HomePage
                self.app.show_page("HomePage")
            else:
                QMessageBox.critical(self, "Login Failed", "Invalid username or password")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {e}")