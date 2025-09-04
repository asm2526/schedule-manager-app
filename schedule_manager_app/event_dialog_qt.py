from PySide6.QtWidgets import (
    QDialog, QLineEdit, QDateEdit, QTimeEdit, QDialogButtonBox,
    QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import QDate, QTime


class EventDialog(QDialog):
    """Google Calendar–style dialog for adding/editing events."""

    def __init__(self, parent, title="", date=None, start_time=None, end_time=None, event_id=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Event" if event_id else "Add Event")
        self.event_id = event_id
        self.deleted = False

        main_layout = QVBoxLayout()

        # --- Title (prominent at top) ---
        self.title_input = QLineEdit(title)
        self.title_input.setPlaceholderText("Add Title")
        self.title_input.setStyleSheet("font-size: 18px; padding: 6px;")
        main_layout.addWidget(self.title_input)

        # --- Date picker ---
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        if date:
            self.date_input.setDate(QDate.fromString(date, "yyyy-MM-dd"))
        main_layout.addWidget(self.date_input)

        # --- Time row (Start / End) ---
        time_layout = QHBoxLayout()

        self.start_input = QTimeEdit()
        self.start_input.setDisplayFormat("hh:mm AP")  # ✅ AM/PM format
        self.start_input.setTime(QTime.currentTime())

        self.end_input = QTimeEdit()
        self.end_input.setDisplayFormat("hh:mm AP")
        self.end_input.setTime(QTime.currentTime().addSecs(3600))

        time_layout.addWidget(QLabel("Start:"))
        time_layout.addWidget(self.start_input)
        time_layout.addWidget(QLabel("End:"))
        time_layout.addWidget(self.end_input)

        main_layout.addLayout(time_layout)

        # --- Initialize times if provided ---
        if start_time:
            self.start_input.setTime(self.parse_time_str(start_time))
        if end_time:
            self.end_input.setTime(self.parse_time_str(end_time))

        # --- Save / Cancel buttons ---
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        # --- Delete button if editing ---
        if event_id:
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("color: red;")
            delete_btn.clicked.connect(self.delete_event)
            main_layout.addWidget(delete_btn)

        self.setLayout(main_layout)

    # ------------------------------------------------------
    # UTILITIES
    # ------------------------------------------------------
    def parse_time_str(self, time_str: str) -> QTime:
        """Parse 'hh:mm AM/PM' into QTime safely."""
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

    # ------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------
    def delete_event(self):
        """Confirm and mark event for deletion."""
        confirm = QMessageBox.question(self, "Delete Event", "Are you sure you want to delete this event?")
        if confirm == QMessageBox.Yes:
            self.deleted = True
            self.accept()

    def get_data(self):
        """Return structured event data."""
        date_str = self.date_input.date().toString("yyyy-MM-dd")
        start_time = self.start_input.time().toString("hh:mm AP")
        end_time = self.end_input.time().toString("hh:mm AP")

        return {
            "title": self.title_input.text().strip(),
            "date": date_str,
            "start": start_time,
            "end": end_time,
            "deleted": self.deleted,
        }
