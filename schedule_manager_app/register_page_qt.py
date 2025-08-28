from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import database

class RegisterPage(QWidget):
    """Registration Screen for new users."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Register New Account"))

        #username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        layout.addWidget(self.username_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Confirm password
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)

        # Register button
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.handle_register)
        layout.addWidget(register_btn)

        # Back to Login
        back_btn = QPushButton("Back to Login")
        back_btn.clicked.connect(lambda: app.show_page("LoginPage"))
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def handle_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not username or not password or not confirm:
            QMessageBox.warning(self, "Missing Info", "All fields are required")
            return
        if password != confirm:
            QMessageBox.warning(self, "Error", "Paswwords do not match")
            return
        
        try:
            if database.create_user(username, password):
                QMessageBox.information(self, "Success", "Account Created! Please log in")
                self.app.show_page("LoginPage")
            else:
                QMessageBox.critical(self, "Error", "Username already exists.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not register: {e}")

            