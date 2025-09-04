from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCalendarWidget
from PySide6.QtCore import QDate
import database
from views.day_view_qt import DayView
from event_dialog_qt import EventDialog


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

    # ------------------------------------------------------
    # VIEW SWITCHING
    # ------------------------------------------------------
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
        self.day_view = DayView(self, self.current_date)   # ✅ FIXED: store reference
        self.day_view.eventDoubleClicked.connect(self.edit_event)  # ✅ FIXED: connect signal

        username = self.app.current_user
        if username:
            date_str = self.current_date.toString("yyyy-MM-dd")
            events = database.get_events_for_day(username, date_str)
            self.day_view.load_events(events)

        self.replace_content(self.day_view)

    # ------------------------------------------------------
    # EVENT HANDLING
    # ------------------------------------------------------
    def add_event(self):
        """Open EventDialog to add a new event for the current date."""
        if not self.app.current_user:
            return

        dlg = EventDialog(self, date=self.current_date.toString("yyyy-MM-dd"))
        if dlg.exec():
            data = dlg.get_data()
            if not data["title"]:
                return
            database.add_event(
                self.app.current_user,
                data["title"],
                data["date"],
                data["start"],
                data["end"],
            )
            self.refresh_day_view()   # ✅ FIXED: refresh after add

    def edit_event(self, event_id: int):
        """Open EventDialog to edit/delete an event."""
        ev = database.get_event(event_id)
        if not ev:
            return

        _, _, title, date, start, end = ev

        dlg = EventDialog(self, title, date, start, end, event_id=event_id)
        if dlg.exec():
            data = dlg.get_data()
            if data["deleted"]:
                database.delete_event(event_id)
            else:
                if not data["title"]:
                    return
                database.update_event(
                    event_id,
                    data["title"],
                    data["date"],
                    data["start"],
                    data["end"],
                )
            self.refresh_day_view()   # ✅ FIXED: refresh after edit/delete

    def refresh_day_view(self):
        """Reload events into the current DayView."""
        if not hasattr(self, "day_view"):
            return
        username = self.app.current_user
        if not username:
            return
        date_str = self.current_date.toString("yyyy-MM-dd")   # ✅ FIXED: corrected format
        events = database.get_events_for_day(username, date_str)
        self.day_view.load_events(events)

    # ------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------
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
