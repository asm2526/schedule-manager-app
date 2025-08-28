from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)

class HomePage(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Home Page"))

        btn_today = QPushButton("Today's Schedule")
        btn_today.clicked.connect(lambda: app.show_page("TodayPage"))
        layout.addWidget(btn_today)

        btn_calendar = QPushButton("View Calendar")
        btn_calendar.clicked.connect(lambda: print("TODO: Implement CalendarPage"))
        layout.addWidget(btn_calendar)

        btn_logout = QPushButton("Logout")
        btn_logout.clicked.connect(lambda: app.show_page("LoginPage"))
        layout.addWidget(btn_logout)

        self.setLayout(layout)
