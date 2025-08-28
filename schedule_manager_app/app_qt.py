import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLabel, QPushButton
)

from login_page_qt import LoginPage

"""
class LoginPage(QWidget):
    def __init__(self, app):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Login Page"))
        btn = QPushButton("Go to Home")
        btn.clicked.connect(lambda: app.show_page("HomePage"))
        layout.addWidget(btn)
        self.setLayout(layout)
"""

class HomePage(QWidget):
    def __init__(self, app):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Home Page"))
        btn = QPushButton("Go to Today")
        btn.clicked.connect(lambda:app.show_page("TodayPage"))
        layout.addWidget(btn)
        self.setLayout(layout)

class TodayPage(QWidget):
    def __init__(self, app):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Today Page (Timeline will go here)"))
        btn = QPushButton("Back to Home")
        btn.clicked.connect(lambda: app.show_page("HomePage"))
        layout.addWidget(btn)
        self.setLayout(layout)

class ScheduleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schedule Manager (Qt)")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.resize(600,400)

        # Instantiate pages
        self.pages = {
            "LoginPage": LoginPage(self),
            "HomePage": HomePage(self),
            "TodayPage": TodayPage(self),
        }

        for name, page in self.pages.items():
            self.stack.addWidget(page)

        self.show_page("LoginPage")

    def show_page(self, name: str):
        page = self.pages.get(name)
        if page:
            self.stack.setCurrentWidget(page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScheduleApp()
    window.show()
    sys.exit(app.exec())