from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCalendarWidget,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import QDate
import database
from event_dialog_qt import EventDialog

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
        self.day_btn.clicked.connect(lambda: self.switch_view("day"))
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
        """Display events for current_date"""
        container = QVBoxLayout()
        wrapper = QWidget()
        wrapper.setLayout(container)

        # date header
        header = QLabel(self.current_date.toString("MMMM d, yyyy"))
        header.setStyleSheet("font-size 18px; font-weight: bold;")
        container.addWidget(header)

        # Events list
        self.event_list = QListWidget()
        self.event_list.itemDoubleClicked.connect(self.edit_event)
        container.addWidget(self.event_list)

        # refresh events
        self.load_events()

        self.replace_content(wrapper)


    def load_events(self):
        """Load events from DB for the current date"""
        self.event_list.clear()
        username = self.app.current_user
        if not username:
            return
        
        date_str = self.current_date.toString("yyyy-MM-dd")
        rows = database.get_events_for_day(username, date_str)

        for ev_id, title, start, end in rows:
            item = QListWidgetItem(f"{start} - {end} | {title}")
            item.setData(1000, ev_id) # store event ID
            self.event_list.addItem(item)

    def add_event(self):
        """open dialog to add event for the current date"""
        if not self.app.current_user:
            return
        
        dlg = EventDialog(self, date=self.current_date.toString("yyyy-MM-dd"))
        if dlg.exec():
            data = dlg.get_data()
            if not data["title"]:
                return
            database.add_event(self.app.current_user, data["title"], data["date"], data["start"], data["end"])
            self.load_events()
        
    def edit_event(self, item):
        event_id = item.data(1000)
        ev = database.get_event(event_id)
        if not ev:
            return
        
        _, _, title, date, start, end=ev

        dlg = EventDialog(self, title, date, start, end, event_id=event_id)
        if dlg.exec():
            data = dlg.get_data()
            if data["deleted"]:
                database.delete_event(event_id)
            else:
                if not data["title"]:
                    return
                database.update_event(event_id, data["title"], data["date"], data["start"], data["end"])
            self.load_events()

    """Helpers"""


    def on_date_selected(self):
        """When a date is clicked in month view"""
        cal: QCalendarWidget = self.content
        self.current_date = cal.selectedDate()
        self.switch_view("day") # automatically jump to day view

    def replace_content(self, widget):
        """Replace central widget area with a new widget"""
        if self.content:
            self.layout().removeWidget(self.content)
            self.content.deleteLater()
        self.content = widget
        self.layout().addWidget(self.content)