# calendar_page_qt.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCalendarWidget
from PySide6.QtCore import QDate
import database
from views.day_view_qt import DayView   # ✅ NEW


class CalendarPage(QWidget):
    """Main calendar page with month/week/day toggle views."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current_date = QDate.currentDate()
        self.current_view = "month"

        layout = QVBoxLayout()

        # Toolbar
        toolbar = QHBoxLayout()
        self.month_btn = QPushButton("Month View")
        self.week_btn = QPushButton("Week View")
        self.day_btn = QPushButton("Day View")
        self.add_btn = QPushButton("Add Event")

        self.month_btn.clicked.connect(lambda: self.switch_view("month"))
        self.week_btn.clicked.connect(lambda: self.switch_view("week"))
        self.day_btn.clicked.connect(lambda: self.switch_view("day"))
        self.add_btn.clicked.connect(self.add_event)

        toolbar.addWidget(self.month_btn)
        toolbar.addWidget(self.week_btn)
        toolbar.addWidget(self.day_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.add_btn)

        layout.addLayout(toolbar)

        self.content = QLabel("Calendar will render here")
        layout.addWidget(self.content)
        self.setLayout(layout)

        self.switch_view("month")

    def switch_view(self, view_type: str):
        self.current_view = view_type
        if view_type == "month":
            self.show_month_view()
        elif view_type == "week":
            self.show_week_view()
        elif view_type == "day":
            self.show_day_view()

    def show_month_view(self):
        cal = QCalendarWidget()
        cal.setSelectedDate(self.current_date)
        cal.selectionChanged.connect(self.on_date_selected)
        self.replace_content(cal)

    def show_week_view(self):
        self.replace_content(QLabel("Week View (Coming Soon)"))

    def show_day_view(self):
        """Use DayView widget and load events from DB."""
        day_view = DayView(self, self.current_date)
        # Fetch events for this date
        username = self.app.current_user
        if username:
            date_str = self.current_date.toString("yyyy-MM-dd")
            events = database.get_events_for_day(username, date_str)
            day_view.load_events(events)
        self.replace_content(day_view)

    def add_event(self):
        print("TODO: Hook EventDialog here")

    def on_date_selected(self):
        cal: QCalendarWidget = self.content
        self.current_date = cal.selectedDate()
        self.switch_view("day")

    def replace_content(self, widget):
        if self.content:
            self.layout().removeWidget(self.content)
            self.content.deleteLater()
        self.content = widget
        self.layout().addWidget(self.content)
