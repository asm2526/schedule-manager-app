from tkinter import ttk

def apply_style(style: ttk.Style) -> None:
    """Centralized ttk style config"""

    try:
        style.theme_use("clam")
    except Exception:
        pass

    #Frames
    style.configure("TFrame", padding=8)

    #Labels
    style.configure("TLabel", padding=(2,1))

    #Buttons
    style.configure(
        "TButton",
        padding=(10,6),
        font=("Segoe UI", 10)
    )
    style.map("TButton",
        relief=[("pressed", "sunken"), ("!pressed", "raised")],
        background=[("active", "#d9e6f2")]
    )

    #Entries
    style.configure("TEntry", padding=4)

    # Scrollbars
    style.configure("Vertical.TScrollbar", arrowsize=12)
    style.configure("Horizontal.TScrollbar", arrowsize=12)