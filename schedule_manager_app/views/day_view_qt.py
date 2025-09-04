from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QTime, QRectF, Signal
from PySide6.QtGui import QPen, QColor


# ✅ NEW: EventBox subclass to emit double-click signal
class EventBox(QGraphicsRectItem):
    def __init__(self, event_id, rect, parent=None):
        super().__init__(rect)
        self.event_id = event_id
        self.setAcceptHoverEvents(True)

    def mouseDoubleClickEvent(self, event):
        # emit signal up to DayView’s parent (CalendarPage listens there)
        self.scene().views()[0].parent().eventDoubleClicked.emit(self.event_id)
        super().mouseDoubleClickEvent(event)


class DayView(QWidget):
    """Minute-precision day view with Google Calendar-style event boxes."""

    # ✅ Signal that CalendarPage connects to
    eventDoubleClicked = Signal(int)

    def __init__(self, parent=None, date=None):
        super().__init__(parent)
        self.date = date
        self.pixels_per_minute = 2
        self.time_column_width = 80
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        layout = QVBoxLayout()
        self.header = QLabel(self.date.toString("MMMM d, yyyy") if self.date else "")
        self.header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.header)
        layout.addWidget(self.view)
        self.setLayout(layout)

        self._draw_time_labels()

    def _draw_time_labels(self):
        """Draw timeline column with labels and divider line."""
        for hour in range(24):
            y = hour * 60 * self.pixels_per_minute
            label = QTime(hour, 0).toString("h AP")
            text = self.scene.addText(label)
            text.setDefaultTextColor(Qt.gray)
            text.setPos(5, y)
        # vertical divider
        self.scene.addLine(self.time_column_width, 0,
                           self.time_column_width, 24 * 60 * self.pixels_per_minute,
                           QPen(QColor("gray")))

    def load_events(self, events: list[tuple]):
        """
        Draw events as EventBox items.
        events = [(id, title, start, end), ...]
        """
        # remove old EventBox items
        for item in self.scene.items():
            if isinstance(item, QGraphicsRectItem):
                self.scene.removeItem(item)

        blocks = []
        for ev_id, title, start, end in events:
            start_qt = self._parse_time(start)
            end_qt = self._parse_time(end)
            start_min = start_qt.hour() * 60 + start_qt.minute()
            end_min = end_qt.hour() * 60 + end_qt.minute()
            duration = max(1, end_min - start_min)
            blocks.append((ev_id, title, start, end, start_min, duration))

        # naive overlap: put each event in its own column if overlapping
        columns = []
        for block in sorted(blocks, key=lambda x: x[4]):
            placed = False
            for col in columns:
                if col[-1][4] + col[-1][5] <= block[4]:
                    col.append(block)
                    placed = True
                    break
            if not placed:
                columns.append([block])

        col_width = 300 / max(1, len(columns))  # width for events

        for col_index, col in enumerate(columns):
            for ev_id, title, start, end, start_min, duration in col:
                x = self.time_column_width + col_index * col_width
                y = start_min * self.pixels_per_minute
                h = duration * self.pixels_per_minute

                # ✅ Use EventBox instead of plain QGraphicsRectItem
                event_box = EventBox(ev_id, QRectF(x, y, col_width, h))
                event_box.setBrush(Qt.cyan)
                event_box.setPen(QPen(QColor("black")))
                self.scene.addItem(event_box)

                text = QGraphicsTextItem(f"{title}\n{start} - {end}")
                text.setDefaultTextColor(Qt.black)
                text.setPos(x + 5, y + 5)
                self.scene.addItem(text)

        self.scene.setSceneRect(0, 0, 600, 24 * 60 * self.pixels_per_minute)

    def _parse_time(self, time_str: str) -> QTime:
        try:
            parts = time_str.strip().split()
            hh, mm = map(int, parts[0].split(":"))
            ampm = parts[1].upper()
            if ampm == "PM" and hh != 12:
                hh += 12
            if ampm == "AM" and hh == 12:
                hh = 0
            return QTime(hh, mm)
        except Exception:
            return QTime.currentTime()
