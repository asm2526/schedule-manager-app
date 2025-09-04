"""New skeleton code to begin new implementation"""
# app_qt.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import Qt

from login_page_qt import LoginPage
from register_page_qt import RegisterPage
from calendar_page_qt import CalendarPage

# placeholders for now
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

"""
class CalendarPage(QWidget):
    def __init__(self, app):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Calendar Page (placehoder)"))
        self.setLayout(layout)
"""

class ScheduleApp(QMainWindow):
    """Main app window managing all pages"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schedule Manager")
        self.resize(1000, 700) # resizable by default

        # Track the logged-in user
        self.current_user: str | None = None

        #page container
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Instantiate pages
        self.pages = {
            "LoginPage": LoginPage(self),
            "RegisterPage": RegisterPage(self),
            "CalendarPage": CalendarPage(self),
        }

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.show_page("LoginPage")

    def show_page(self, name: str):
        """Switch to a page by name if it exists, and refresh if supported"""
        page = self.pages.get(name)
        if page:
            self.stack.setCurrentWidget(page)
            if hasattr(page, "refresh"):
                page.refresh()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    #Enable high DPI scaling + strackpad/mousewheel smoothness
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setStyle("Fusion")  # modern look

    window = ScheduleApp()
    window.show()
    sys.exit(app.exec())
