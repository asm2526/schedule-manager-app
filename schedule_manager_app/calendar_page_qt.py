from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCalendarWidget
)
from PySide6.QtCore import QDate

class CalendarPage(QWidget):
    """Main calendar page with month/week/day toggle views"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current_date = QDate.currentDate() # track selected date
        self.current_view = "month"

        layout = QVBoxLayout()

        # Toolbar
        toolbar = QHBoxLayout()

        self.month_btn = QPushButton("Month View")
        self.week_btn = QPushButton("Week View")
        self.day_btn = QPushButton("Day View")
        self.add_btn = QPushButton("Add Event")

        # Connect buttons
        self.month_btn.clicked.connect(lambda: self.switch_view("month"))
        self.week_btn.clicked.connect(lambda: self.switch_view("week"))
        self.day_btn.clicked.connect(lambda: self.switch_View("day"))
        self.add_btn.clicked.connect(self.add_event)

        toolbar.addWidget(self.month_btn)
        toolbar.addWidget(self.week_btn)
        toolbar.addWidget(self.day_btn)
        toolbar.addStretch() # pushes add event to the right
        toolbar.addWidget(self.add_btn)

        layout.addLayout(toolbar)

        # Content area (dynamic)
        self.content = QLabel("Calendar will render here")
        layout.addWidget(self.content)

        self.setLayout(layout)

        # start with month view
        self.switch_view("month")

    def switch_view(self, view_type: str):
        """switch between month week day views"""
        self.current_view = view_type
        if view_type == "month":
            self.show_month_view()
        elif view_type == "week":
            self.show_week_view()
        elif view_type == "day":
            self.show_day_view()

    def show_month_view(self):
        """Display mont calendar"""
        cal = QCalendarWidget()
        cal.setSelectedDate(self.current_date)
        cal.selectionChanged.connect(self.on_date_selected)
        self.replace_content(cal)

    def show_week_view(self):
        """placeholder for week view"""
        self.replace_content(QLabel("week view coming soon"))

    def show_day_view(self):
        """placeholder for day view"""
        self.replace_content(QLabel(f"Day view for {self.current_date.toString('MMMM d, yyyy')}"))

    def on_date_selected(self):
        """When a date is clicked in month view"""
        cal: QCalendarWidget = self.content
        self.current_date = cal.selectedDate()
        self.switch_view("day") # automatically jump to day view

    def add_event(self):
        """Global add event button will open dialog"""
        print(f"Add event clicked for {self.current_date.toString('yyy-MM-dd')} (TODO)")

    def replace_content(self, widget):
        """Replace central widget area with a new widget"""
        if self.content:
            self.layout().removeWidget(self.content)
            self.content.deleteLater()
        self.content = widget
        self.layout().addWidget(self.content)