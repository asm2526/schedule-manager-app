# schedule_manager_app/ui/pages/today_page.py
import os, sys
from datetime import date, datetime

import tkinter as tk
from tkinter import ttk, messagebox

# Import the reusable 12h timeline widget
from schedule_manager_app.ui.widgets.timeline import Timeline12h

# Import your existing root-level database.py (unchanged for now)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import database  # expects: add_event, get_event, update_event, delete_event, get_events_for_day


# ---- Minimal modal popup for Edit/Delete (12-hour inputs) ----
class EventEditor(tk.Toplevel):
    """
    Modal popup to edit or delete an event (Title / Time HH:MM / AM-PM / Duration).
    Result:
      - None (cancel) OR
      - {"action":"delete"} OR
      - {"action":"save","title":str,"time_12h":"HH:MM","ampm":"AM|PM","duration":int}
    """
    def __init__(self, parent, *, title: str, time_12h: str, ampm: str, duration: int):
        super().__init__(parent)
        self.transient(parent)
        self.title("Edit Event")
        self.resizable(False, False)
        self.result = None

        self.bind("<Escape>", lambda _e: self._cancel())

        frm = ttk.Frame(self, padding=14)
        frm.pack(fill="both", expand=True)

        # Title
        ttk.Label(frm, text="Title").grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar(value=title)
        ttk.Entry(frm, textvariable=self.title_var, width=36).grid(row=1, column=0, columnspan=3, sticky="ew", pady=(2, 10))

        # Time + AM/PM
        ttk.Label(frm, text="Time (HH:MM)").grid(row=2, column=0, sticky="w")
        self.time_var = tk.StringVar(value=time_12h)
        ttk.Entry(frm, textvariable=self.time_var, width=8).grid(row=3, column=0, sticky="w", pady=(2, 10))

        ttk.Label(frm, text="AM/PM").grid(row=2, column=1, sticky="w", padx=(10, 0))
        self.ampm_var = tk.StringVar(value=(ampm or "AM").upper())
        ampm_box = ttk.Combobox(frm, textvariable=self.ampm_var, values=["AM", "PM"], width=5, state="readonly")
        ampm_box.grid(row=3, column=1, sticky="w", padx=(10, 0), pady=(2, 10))

        # Duration
        ttk.Label(frm, text="Duration (minutes)").grid(row=2, column=2, sticky="w", padx=(10, 0))
        self.dur_var = tk.StringVar(value=str(duration))
        ttk.Entry(frm, textvariable=self.dur_var, width=8).grid(row=3, column=2, sticky="w", padx=(10, 0), pady=(2, 10))

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=3, sticky="e", pady=(6, 0))
        ttk.Button(btns, text="Delete", command=self._delete).pack(side="left")
        ttk.Button(btns, text="Cancel", command=self._cancel).pack(side="right", padx=(6, 0))
        ttk.Button(btns, text="Save", command=self._save).pack(side="right")

        frm.columnconfigure(0, weight=1)

        self._center(parent)
        self.grab_set()
        self.focus()

    def _center(self, parent):
        self.update_idletasks()
        try:
            px, py = parent.winfo_rootx(), parent.winfo_rooty()
            pw, ph = parent.winfo_width(), parent.winfo_height()
        except Exception:
            px = py = 100; pw = ph = 300
        w, h = self.winfo_width(), self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _delete(self):
        if messagebox.askyesno("Delete", "Delete this event?", parent=self):
            self.result = {"action": "delete"}
            self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()

    def _save(self):
        title = (self.title_var.get() or "").strip()
        ampm = (self.ampm_var.get() or "AM").upper()
        time_12h = (self.time_var.get() or "12:00").strip()
        dur_txt = (self.dur_var.get() or "60").strip()

        if not title:
            messagebox.showwarning("Missing", "Title is required.", parent=self)
            return

        # Validate time HH:MM (12h)
        try:
            h12, m = map(int, time_12h.split(":"))
            if not (1 <= h12 <= 12) or not (0 <= m < 60):
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid time", "Time must be HH:MM in 12-hour format.", parent=self)
            return

        try:
            duration = int(dur_txt)
            if duration <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid duration", "Duration must be a positive integer.", parent=self)
            return

        self.result = {
            "action": "save",
            "title": title,
            "time_12h": f"{h12:02d}:{m:02d}",
            "ampm": ampm,
            "duration": duration,
        }
        self.destroy()


# ---- Today Page ----
class TodayPage(ttk.Frame):
    """
    Shows today's events on a 12-hour labeled timeline.
    - Add event via button (uses the same popup flow with empty defaults)
    - Click an event to open the EventEditor popup (Save/Delete)
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=12, pady=(12, 6))

        ttk.Label(header, text="Today's Schedule").pack(side="left")

        ttk.Button(header, text="Add Event",
                   command=self._add_event).pack(side="right", padx=(4, 0))
        ttk.Button(header, text="Back",
                   command=lambda: controller.show_frame("HomePage")).pack(side="right")

        # 12-hour timeline
        self.timeline = Timeline12h(self, pixels_per_hour=60, on_event_click=self._on_event_click)
        self.timeline.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self._today_iso = date.today().isoformat()

    def on_show(self):
        self._refresh()

    # -------- Helpers --------
    def _refresh(self):
        username = self.controller.current_user
        if not username:
            return
        try:
            rows = database.get_events_for_day(username, self._today_iso)
            # Expecting rows of (id, title, start_iso, duration_minutes)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load events: {e}")
            return

        # Convert to simple objects the timeline expects
        class E: ...
        events = []
        for r in rows:
            ev = E()
            ev.id, ev.title, ev.start_iso, ev.duration_minutes = r
            events.append(ev)

        self.timeline.set_date_and_events(self._today_iso, events)

        # auto-scroll to 'now'
        now = datetime.now()
        self.timeline.scroll_to_time(now.hour, now.minute)

    def _add_event(self):
        username = self.controller.current_user
        if not username:
            messagebox.showwarning("Not logged in", "Please log in first.")
            return

        # empty defaults
        dlg = EventEditor(self, title="", time_12h="09:00", ampm="AM", duration=60)
        self.wait_window(dlg)
        if not dlg.result or dlg.result["action"] != "save":
            return

        # Convert 12h -> 24h and add
        t12 = dlg.result["time_12h"]
        ampm = dlg.result["ampm"]
        hh12, mm = map(int, t12.split(":"))
        h24 = hh12 % 12
        if ampm == "PM":
            h24 += 12
        if ampm == "AM" and hh12 == 12:
            h24 = 0
        start_iso = f"{self._today_iso} {h24:02d}:{mm:02d}"

        try:
            database.add_event(username, dlg.result["title"].strip(), start_iso, int(dlg.result["duration"]))
            self._refresh()
        except Exception as e:
            messagebox.showerror("Could not add", f"{e}")

    def _on_event_click(self, event_id: int):
        # Load the event
        try:
            row = database.get_event(event_id)  # (id, username, title, start_iso, duration_minutes)
            if not row:
                messagebox.showerror("Not found", "Event no longer exists.")
                return
            _, _, title, start_iso, duration = row
        except Exception as e:
            messagebox.showerror("Error", f"Could not load event: {e}")
            return

        # Prefill as 12h
        date_iso, hm = start_iso.split(" ")
        h24, m = map(int, hm.split(":"))
        if h24 == 0:        h12, ampm = 12, "AM"
        elif h24 < 12:      h12, ampm = h24, "AM"
        elif h24 == 12:     h12, ampm = 12, "PM"
        else:               h12, ampm = h24 - 12, "PM"

        dlg = EventEditor(self, title=title, time_12h=f"{h12:02d}:{m:02d}", ampm=ampm, duration=duration)
        self.wait_window(dlg)
        if not dlg.result:
            return

        if dlg.result["action"] == "delete":
            try:
                if database.delete_event(event_id):
                    self._refresh()
                else:
                    messagebox.showwarning("Not deleted", "Event may not exist.")
            except Exception as e:
                messagebox.showerror("Could not delete", f"{e}")
            return

        if dlg.result["action"] == "save":
            # 12h -> 24h and update
            t12 = dlg.result["time_12h"]
            ampm = dlg.result["ampm"]
            hh12, mm = map(int, t12.split(":"))
            h24 = hh12 % 12
            if ampm == "PM":
                h24 += 12
            if ampm == "AM" and hh12 == 12:
                h24 = 0
            new_start_iso = f"{date_iso} {h24:02d}:{mm:02d}"

            try:
                ok = database.update_event(
                    event_id,
                    title=dlg.result["title"].strip(),
                    start_iso=new_start_iso,
                    duration_minutes=int(dlg.result["duration"]),
                )
                if not ok:
                    messagebox.showwarning("No change", "Nothing was updated.")
                self._refresh()
            except Exception as e:
                messagebox.showerror("Could not update", f"{e}")
