# views/day_view_qt.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView
from PySide6.QtCore import Qt, QTime, Signal


class DayView(QWidget):
    """UI widget for displaying one day's schedule in a 24-hour timeline."""

    # new signal emitted when user double-clicks an event
    eventDoubleClicked = Signal(int) # event id

    def __init__(self, parent=None, date=None):
        super().__init__(parent)
        self.date = date
        self.table = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        # Header with the date
        self.header = QLabel(self.date.toString("MMMM d, yyyy") if self.date else "")
        self.header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.header)

        # Timeline grid (24 rows, one per hour)
        self.table = QTableWidget(24, 2)
        self.table.setHorizontalHeaderLabels(["Time", "Events"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 80)

        # Fill left column with times
        for hour in range(24):
            label_time = QTime(hour, 0).toString("h AP")  # "12 AM", "1 AM", etc.
            self.table.setItem(hour, 0, QTableWidgetItem(label_time))

        self.table.cellDoubleClicked.connect(self._handle_double_click)
        
        layout.addWidget(self.table)
        self.setLayout(layout)

    # ------------------------------------------------------
    # Public API for CalendarPage (controller) to call
    # ------------------------------------------------------
    def set_date(self, date):
        """Update header and internal date."""
        self.date = date
        self.header.setText(date.toString("MMMM d, yyyy"))

    def load_events(self, events: list[tuple]):
        """
        Fill the table with events.
        events = [(id, title, start, end), ...]
        start/end = "hh:mm AM/PM"
        """
        self.table.clearContents()

        for ev_id, title, start, end in events:
            # For now, just show the event on the row for its start hour
            start_hour = self._parse_time(start).hour()
            item = QTableWidgetItem(f"{start} - {end} | {title}")
            item.setData(Qt.UserRole, ev_id)
            self.table.setItem(start_hour, 1, item)

    def _handle_double_click(self, row, col):
        item = self.table.item(row, col)
        if not item:
            return
        event_id = item.data(Qt.UserRole)
        if event_id:
            self.eventDoubleClicked.emit(event_id)

    def _parse_time(self, time_str: str) -> QTime:
        """Convert 'hh:mm AM/PM' into QTime safely."""
        try:
            parts = time_str.strip().split()
            hh, mm = map(int, parts[0].split(":"))
            ampm = parts[1].upper() if len(parts) > 1 else "AM"
            if ampm == "PM" and hh != 12:
                hh += 12
            if ampm == "AM" and hh == 12:
                hh = 0
            return QTime(hh, mm)
        except Exception:
            return QTime.currentTime()
