# today_page_qt.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QLineEdit, QDateTimeEdit, QDialogButtonBox, QFormLayout,
    QMessageBox
)
from PySide6.QtCore import QDateTime
import database


class EventDialog(QDialog):
    """Dialog for adding or editing an event."""

    def __init__(self, parent, title="", start_iso=None, end_iso=None, event_id=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Event" if event_id else "Add Event")
        self.event_id = event_id  # None = add mode, not None = edit mode

        layout = QFormLayout()

        # Title input
        self.title_input = QLineEdit(title)
        layout.addRow("Title:", self.title_input)

        # Start datetime
        self.start_input = QDateTimeEdit()
        self.start_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.start_input.setCalendarPopup(True)
        layout.addRow("Start Time:", self.start_input)

        # End datetime
        self.end_input = QDateTimeEdit()
        self.end_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.end_input.setCalendarPopup(True)
        layout.addRow("End Time:", self.end_input)

        # Initialize with provided times
        if start_iso:
            self.start_input.setDateTime(QDateTime.fromString(start_iso, "yyyy-MM-dd HH:mm"))
        else:
            self.start_input.setDateTime(QDateTime.currentDateTime())

        if end_iso:
            self.end_input.setDateTime(QDateTime.fromString(end_iso, "yyyy-MM-dd HH:mm"))
        else:
            self.end_input.setDateTime(QDateTime.currentDateTime().addSecs(3600))

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        # Optional delete button if editing
        if event_id:
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(self.delete_event)
            layout.addWidget(delete_btn)

        self.setLayout(layout)

        self.deleted = False  # Track if user clicked delete

    def delete_event(self):
        """Mark this event for deletion and close dialog."""
        confirm = QMessageBox.question(self, "Delete Event", "Are you sure you want to delete this event?")
        if confirm == QMessageBox.Yes:
            self.deleted = True
            self.accept()

    def get_data(self):
        return {
            "title": self.title_input.text().strip(),
            "start": self.start_input.dateTime().toString("yyyy-MM-dd HH:mm"),
            "end": self.end_input.dateTime().toString("yyyy-MM-dd HH:mm"),
            "deleted": self.deleted,
        }


class TodayPage(QWidget):
    """Page to display and manage today's events."""

    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Today's Schedule"))

        # Add Event button
        add_btn = QPushButton("Add Event")
        add_btn.clicked.connect(self.add_event)
        layout.addWidget(add_btn)

        # Back to Home button
        back_btn = QPushButton("Back to Home")
        back_btn.clicked.connect(lambda: app.show_page("HomePage"))
        layout.addWidget(back_btn)

        # Timeline table
        self.table = QTableWidget(24, 1)
        self.table.setHorizontalHeaderLabels(["Events"])
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(30)

        # Label rows by hour
        for hour in range(24):
            self.table.setVerticalHeaderItem(hour, QTableWidgetItem(f"{hour:02d}:00"))

        # Double-click to edit
        self.table.cellDoubleClicked.connect(self.edit_event)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def refresh(self):
        """Load today's events from DB and populate table."""
        username = self.app.current_user
        if not username:
            return

        today = QDateTime.currentDateTime().toString("yyyy-MM-dd")
        rows = database.get_events_for_day(username, today)

        # Clear table
        for row in range(24):
            self.table.setItem(row, 0, QTableWidgetItem(""))

        # Fill events
        for ev_id, title, start_iso, end_iso in rows:
            hour = int(start_iso.split(" ")[1].split(":")[0])
            item = QTableWidgetItem(title)
            item.setData(1000, ev_id)  # store event_id in custom role
            self.table.setItem(hour, 0, item)

    def add_event(self):
        """Open dialog to add a new event."""
        if not self.app.current_user:
            return

        dlg = EventDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            if not data["title"]:
                return
            database.add_event(self.app.current_user, data["title"], data["start"], data["end"])
            self.refresh()

    def edit_event(self, row, column):
        """Open dialog to edit or delete an event."""
        item = self.table.item(row, column)
        if not item:
            return

        event_id = item.data(1000)
        ev = database.get_event(event_id)
        if not ev:
            return

        _, _, title, start_iso, end_iso = ev
        dlg = EventDialog(self, title, start_iso, end_iso, event_id=event_id)
        if dlg.exec():
            data = dlg.get_data()
            if data["deleted"]:
                database.delete_event(event_id)
            else:
                if not data["title"]:
                    return
                database.update_event(event_id, data["title"], data["start"], data["end"])
            self.refresh()
