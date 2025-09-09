from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout    
)
from PySide6.QtCore import Qt

class EventDetailsDialog(QDialog):
    """Universal Event Details with exit edit and delete options"""

    def __init__(self, parent=None, event_data=None):
        """
        event_data = {
        "id": int,
        "title": str,
        "start": "hh:mm AM/PM",
        "end": "hh:mm AM/PM",
        "date": "YYYY-MM-DD",
        "description": str,
        "color": str
        "repeat": str
        }
        """
        super().__init__(parent)
        self.setWindowTitle("Event Details")
        self.setMinimumWidth(300)
        self.result_action = None #will hold edit delete or exit
        
        layout = QVBoxLayout()

        #Title
        title = QLabel(event_data.get("title", "Untitled"))
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # date + time
        date_label = QLabel(f"Date: {event_data.get('date', '')}")
        time_label = QLabel(f"Time: {event_data.get('start', '')} - {event_data.get('end', '')}")
        layout.addWidget(date_label)
        layout.addWidget(time_label)

        # Description
        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setPlainText(event_data.get("description", "No description"))
        layout.addWidget(desc)

        # repeat info
        repeat_label = QLabel(f"Repeats: {event_data.get('repeat', 'Does not repeat')}")
        layout.addWidget(repeat_label)

        #Buttons
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")
        exit_btn = QPushButton("Exit")

        edit_btn.clicked.connect(self._edit)
        delete_btn.clicked.connect(self._delete)
        exit_btn.clicked.connect(self._exit)

        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(exit_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    """Button handlers"""
    def _edit(self):
        self.result_action = "edit"
        self.accept()

    def _delete(self):
        self.result_action = "delete"
        self.accept()

    def _exit(self):
        self.result_action = "exit"
        self.reject()

