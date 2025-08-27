# schedule_manager_app/ui/widgets/timeline.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime

__all__ = ["Timeline12h"]


class Timeline12h(ttk.Frame):
    """
    Scrollable, resizable 24-hour vertical timeline that DISPLAYS 12-hour AM/PM labels.
    Expects events with attributes: id, title, start_iso ('YYYY-MM-DD HH:MM'), duration_minutes (int).
    Calls on_event_click(event_id) when an event block is clicked.
    """

    def __init__(self, parent, *, pixels_per_hour=60, on_event_click=None):
        super().__init__(parent)
        self.PPH = pixels_per_hour
        self.on_event_click = on_event_click
        self.events = []
        self.date_iso = None
        self.total_height = 24 * self.PPH

        self.canvas = tk.Canvas(self, height=420, highlightthickness=0)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(
            yscrollcommand=self.vsb.set,
            scrollregion=(0, 0, 800, self.total_height)
        )

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.bind("<Configure>", self._on_resize)
        self._draw_grid()
        self._draw_now_line()  # schedules itself every minute

        self.canvas.bind("<Enter>", lambda _e: self._bind_scroll())
        self.canvas.bind("<Leave>", lambda _e: self._unbind_scroll())

    # ---- Public API ----
    def set_date_and_events(self, date_iso: str, events: list):
        self.date_iso = date_iso
        self.events = events
        self._render_events()

    def scroll_to_time(self, hour: int, minute: int = 0):
        y = int((hour + minute / 60) * self.PPH)
        self.canvas.yview_moveto(max(0, min(1, y / max(1, self.total_height - 1))))

    # ---- Internals ----
    def _on_resize(self, event):
        try:
            sb_w = self.vsb.winfo_width() or 14
        except Exception:
            sb_w = 14
        new_w = max(260, event.width - sb_w - 2)
        self.canvas.config(width=new_w)
        self.canvas.config(scrollregion=(0, 0, new_w, self.total_height))
        self._draw_grid()

    def _label_hour_12h(self, h24: int) -> str:
        ampm = "AM" if h24 < 12 else "PM"
        h = h24 % 12
        if h == 0:
            h = 12
        return f"{h:02d}:00 {ampm}"

    def _label_time_12h(self, h24: int, m: int) -> str:
        ampm = "AM" if h24 < 12 else "PM"
        h = h24 % 12
        if h == 0:
            h = 12
        return f"{h:02d}:{m:02d} {ampm}"

    def _draw_grid(self):
        c = self.canvas
        c.delete("grid")
        width = int(c.cget("width") or 800)

        for h in range(25):
            y = h * self.PPH
            c.create_line(0, y, width, y, fill="#dddddd", tags=("grid",))
            if h < 24:
                c.create_text(8, y + 2, anchor="nw", text=self._label_hour_12h(h),
                              tags=("grid",), fill="#555555")

        # subtle divider between AM and PM
        noon_y = 12 * self.PPH
        c.create_line(0, noon_y, width, noon_y, fill="#bbbbbb", dash=(2, 2), tags=("grid",))

    def _draw_now_line(self):
        c = self.canvas
        c.delete("now")
        now = datetime.now()
        y = int((now.hour + now.minute / 60) * self.PPH)
        width = int(c.cget("width") or 800)
        c.create_line(0, y, width, y, fill="#e53935", width=2, tags=("now",))
        # refresh about once per minute
        self.after(60_000, self._draw_now_line)

    def _render_events(self):
        c = self.canvas
        c.delete("event")
        width = int(c.cget("width") or 800)
        left, right = 90, max(290, width - 20)

        for ev in self.events:
            top = self._y_from_iso(ev.start_iso)
            height = max(18, int(ev.duration_minutes / 60 * self.PPH))
            tags = ("event", f"event-{ev.id}")

            c.create_rectangle(left, top, right, top + height,
                               fill="#cfe8ff", outline="#4a90e2", width=1, tags=tags)

            hh24, mm = map(int, ev.start_iso.split(" ")[1].split(":"))
            label_time = self._label_time_12h(hh24, mm)
            c.create_text(left + 8, top + 4, anchor="nw",
                          text=f"{label_time}  —  {ev.title}",
                          tags=tags, fill="#13334c")

            if callable(self.on_event_click):
                c.tag_bind(f"event-{ev.id}", "<Button-1>",
                           lambda _e, eid=ev.id: self.on_event_click(eid))

    def _y_from_iso(self, iso: str) -> int:
        dt = datetime.strptime(iso, "%Y-%m-%d %H:%M")
        return int((dt.hour + dt.minute / 60) * self.PPH)
    
    def _bind_scroll(self):
        #windows/macos two-finger & wheel scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux x11
        self.canvas.bind_all("<Button-4>", self._on_linux_scroll_up)
        self.canvas.bind_all("<Button-5>", self._on_linux_scroll_up)

    def _unbind_scroll(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        #Normalize delta:
        delta = event.delta or 0
        if abs(delta) >=120:
            units = int(-delta / 120)
        else:
            units = -1 if delta > 0 else (1 if delta < 0 else 0)
        if units:
            self.canvas.yview_scroll(units, "units")

    def _on_linux_scroll_up(self, _event):
        self.canvas.yview_scroll(-1, "units")

    def _on_linux_scroll_down(self, _event):
        self.canvas.yview_scroll(1, "units")


