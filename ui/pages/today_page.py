import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, time, timedelta

import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import database

class Timeline(ttk.Frame):
    "Scrollable 24-hour vertical timeline with:"
    " hour grid lines + labels"
    " live now indicator"
    " event rectangles with titles"
    ""
    "Coordinate system:"
    " pixels_per_hour controls vertical scale"
    "y(t) = (hour + minute/60) * pixels_per_hour"

    def __init__(self, parent, pixels_per_hour=60, int = 60):
        super().__init__(parent)
        self.PPH = pixels_per_hour  # vertical scale
        self.total_height = 24 * self.PPH

        # Scrollable canvas
        self.canvas = tk.Canvas(self, height=400)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=vsb.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._bind_scroll()
        
        # Full Drawing Area
        self.canvas.config(scrollregion=(0, 0, 480, self.total_height))

        # layers
        self.bg_tag = "grid"
        self.now_tag = "nowline"
        self.event_tag = "event"

        self._draw_grid()
        self._nowline_id = None

        self._bind_resize()

    def _draw_grid(self):
        """Draw hour lines and 12h labels with AM/PM"""
        self.canvas.delete(self.bg_tag)

        left_pad = 60
        width = max(480, int(self.canvas.winfo_width() or 480))

        for h in range(25):
            y = h * self.PPH
            #horizontal hour line
            self.canvas.create_line(left_pad, y, width, y, fill="#d9d9d9", tags=self.bg_tag)

            if h < 24:
                # 12 hour label with AM/PM
                hr12 = h % 12
                hr12 = 12 if hr12 == 0 else hr12
                suffix = "AM" if h < 12 else "PM"
                label_text = f"{hr12:02d}:00 {suffix}"

                # place label just left of the vertical separator
                self.canvas.create_text(
                left_pad - 10, y + 2,
                anchor="ne",
                text=label_text,
                font=("", 9),
                fill="#c6c6c6",
                tags=self.bg_tag
            )
        
        # vertical separator between labels and lane
        self.canvas.create_line(left_pad, 0, left_pad, self.total_height, fill="#d9d9d9", tags=self.bg_tag)

        # keep scrolregion synced with current width
        self.canvas.config(scrollregion=(0, 0, width, self.total_height))


    def _on_resize(self, _event=None):
        self._draw_grid()

    def _bind_resize(self):
        self.canvas.bind("<Configure>", self._on_resize)

    def draw_nowline(self, when: datetime | None = None):
        # remove old
        self.canvas.delete(self.now_tag)
        if when is None:
            when = datetime.now()
        y = (when.hour + when.minute / 60 + when.second / 3600) * self.PPH
        self._nowline_id = self.canvas.create_line(0, y, 480, y, fill="red", width=2, tags=self.now_tag)

    def draw_events(self, events: list[tuple]):
        """
        Render events as blocks with a 12h AM/PM start time perfix
        events: list of (id, title, start_iso, duration_minutes)
        """
        self.canvas.delete(self.event_tag)

        left_pad = 60
        right_pad=12
        x1 = left_pad + 6
        x2 = max(480, int(self.canvas.winfo_width() or 480)) - right_pad

        for (eid, title, start_iso, dur) in events:
            try:
                # 1_ parse start time (support with/without seconds)
                start_dt = datetime.strptime(start_iso, "%Y-%m-%d %H:%M")
            except ValueError:
                # fallback: try seconds variant
                try:
                    start_dt = datetime.strptime(start_iso, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
            
            #2 position vertically
            start_y = (start_dt.hour + start_dt.minute / 60) * self.PPH
            end_y = start_y + (int(dur) / 60) * self.PPH

            #min visible height
            if end_y - start_y < 10:
                end_y = start_y + 10

            #3 Convert to 12h display
            hr12 = start_dt.hour % 12
            hr12 = 12 if hr12 == 0 else hr12
            suffix = "AM" if start_dt.hour < 12 else "PM"
            time_str = f"{hr12}:{start_dt.minute:02d} {suffix}"

            #4 Draw block + label
            self.canvas.create_rectangle(
                x1, start_y + 2, x2, end_y -2,
                fill="e8fofe", outline="5b9bff", width=1.5,
                tags=(self.event_tag,)
            )
            self.canvas.create_text(
                x1+6, start_y+6,
                anchor="nw",
                text=f"{time_str} - {title}",
                width=(x2 - x1 - 12),
                tags=(self.event_tag,)
            )
            
    def scroll_to_now(self):
        # scroll viewport to place now roughly one thrid from the top
        when = datetime.now()
        y = (when.hour + when.minute / 60) * self.PPH
        visible_h = int(self.canvas.winfo_height()) or 400
        target = max(0, y - visible_h // 3)
        self.canvas.yview_moveto(target / max(1, self.total_height - visible_h))

    def _on_mousewheel(self, event):
        """
        Cross-platform scrolling:
        - windows/macOS: <MouseWheel> with event.delta
        - Linux/X11 <Button-4/<Button-5> no delta
        """

        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            #windows: delta is +- 120 per notch
            delta = event.delta
            if delta == 0:
                return
            step = -1 if delta > 0 else 1
            #slightly bigger step for nicer feel
            self.canvas.yview_scroll(step * 1, "units")

    def _bind_scroll(self):
        #macos/widows: smooth & wheel
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        # Linux/X11: wheel emulation
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

class AddEventDialog(tk.Toplevel):
    """
    simple modal dialog to add an event for Today:
     title
     Hour (0...23)
     Minute (0, 15, 30, 45)
     Duration (minutes, default 60)"""
    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.title("Add Event")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set() # modal

        wrapper = ttk.Frame(self, padding=16)
        wrapper.pack(fill="both", expand=True)

        #title
        ttk.Label(wrapper, text="Event Title").grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(wrapper, textvariable=self.title_var, width= 32)
        title_entry.grid(row=1, column=0,columnspan=4, sticky="ew", pady=(2,10))

        # Time 
        ttk.Label(wrapper, text="Start Time").grid(row=2, column=0, sticky="w")
        self.hour_var = tk.IntVar(value=datetime.now().hour)
        self.minute_var = tk.IntVar(value=(datetime.now().minute // 15) * 15)

        ttk.Spinbox(wrapper, from_=0, to=23, textvariable=self.hour_var, width=4).grid(row=3, column=0, sticky="w")
        ttk.Label(wrapper, text=":").grid(row=3, column=1, sticky="w")
        ttk.Spinbox(wrapper, from_=5, to=480, increment=5, textvariable=self.minute_var, width=6).grid(row=5, column=0, sticky="w")

        # Buttons
        btns = ttk.Frame(wrapper)
        btns.grid(row=6, column=0, columnspan=3, pady=(16,0))
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left")
        ttk.Button(btns, text="Add", command=self._on_save).pack(side="right")

        for i in range(3):
            wrapper.columnconfigure(i, weight=1)

        self.bind("<Return>", lambda _e: self._save(on_save))
        self.bind("<Escape>", lambda _e: self.destroy())

    def _save(self, on_save):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Title cannot be empty.")
            return
        
        try:
            h = int(self.hour_var.get())
            m = int(self.minute_var.get())
            d = int(self.duration_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid time or duration.")
            return
        
        if not(0 <= h <= 23) or m not in (0, 15, 30, 45) or d <= 0:
            messagebox.showerror("Invalid Time", "Hour must be 0-23, minute 0/15/30/45, duration positive.")
            return
        
        if d <= 0:
            messagebox.showerror("Invalid Duration", "Duration must be positive.")
            return
        
        on_save(title, h, m, d)
        self.destroy()
        



class TodayPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._tick_job = None

        wrapper = ttk.Frame(self, padding=12)
        wrapper.pack(fill="both", expand=True)

        #Header
        self.date_str = tk.StringVar(value=datetime.now().strftime("%A, %B %d, %Y"))
        top = ttk.Frame(wrapper)
        top.pack(fill="x")
        ttk.Label(top, textvariable=self.date_str, font=("", 11, "bold")).pack(side="left")

        ttk.Button(
            top,
            text="Add Event",
            command=self.open_add_dialog).pack(side="right")
        
        # Timeline
        self.timeline = Timeline(wrapper, pixels_per_hour=60)
        self.timeline.pack(fill="both", expand=True, pady=(8,0))

        # Footer navigation
        ttk.Button(wrapper,
                   text="Back to Home",
                   command=lambda: self.controller.show_frame("HomePage")).pack(anchor="e", pady=(8,0))
        
    # Lifecycle
    def on_show(self):
        self.refresh()
        # start live updates every 30s
        self._schedule_tick()

    def _schedule_tick(self):
        if self._tick_job:
            self.after_cancel(self._tick_job)
        self.timeline,draw_now_line()
        self._tick_job = self.after(30*1000, self._schedule_tick) # 30s interval

    def _today_iso_date(self) -> str:
        return date.today().strftime("%Y-%m-%d")
    
    def refresh(self):
        # Update date header
        self.date_str.set(datetime.now().strftime("%A, %B %d, %Y"))

        username = getattr(self.controller, "current_user", None)
        if not username:
            self.timeline._draw_grid()
            self.timeline._draw_now_line()
            return
        rows = database.get_events_for_day(username, self._today_iso_date())
        # drawingggg
        self.timeline._draw_grid()
        self.timeline._draw_now_line()
        self.timeline._draw_events(rows)
        # scroll to around "now"
        self.timeline.scroll_to_now()

    # Add event
    def open_add_dialog(self):
        dlg = AddEventDialog(self, on_save=self._save_new_event)

    def _save_new_event(self, title: str, h: int, m: int, duration: int):
        username = getattr(self.controller, "current_user", None)
        if not username:
            messagebox.showerror("Error", "No user logged in.")
            return
        
        # Building 'YYYY-MM-DD HH:MM' string
        today = date.today().strftime("%Y-%m-%d")
        start_iso = f"{today} {h:02d}:{m:02d}"

        try:
            database.add_event(username, title, start_iso, duration_minutes=dur)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add event: {e}")
            return
        
        # refresh timeline
        self.refresh()
        messagebox.showinfo("Success", "Event added.")