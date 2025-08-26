import tkinter as tk
from tkinter import ttk
from typing import Optional, Union

__all__ = ["apply_style", "center_window", "bring_to_front"]

def apply_style(style: ttk.Style) -> None:
    """Placeholder for future ttk styling."""
    return

def center_window(win: tk.Misc, width: Optional[int] = None, height: Optional[int] = None) -> None:
    win.update_idletasks()
    w = int(width) if width is not None else max(win.winfo_width(), win.winfo_reqwidth())
    h = int(height) if height is not None else max(win.winfo_height(), win.winfo_reqheight())
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = (sh // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def bring_to_front(win: Union[tk.Tk, tk.Toplevel]) -> None:
    try:
        win.lift()
        win.attributes("-topmost", True)
        win.after(300, lambda: win.attributes("-topmost", False))
    except Exception:
        pass