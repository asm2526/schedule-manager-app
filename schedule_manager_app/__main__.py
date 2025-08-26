"""
Run with:
    python3 -m schedule_manager_app
or directly:
    python3 schedule_manager_app/__main__.py
"""

def _load_app_class():
    """Import App whether run as a module or directly"""
    try:
        #normal: python3 -m schedule_manager_app
        from .app import App as _App
        return _App
    except Exception:
        #direct run fallback
        import os, sys
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        parent = os.path.dirname(pkg_dir)
        if parent not in sys.path:
            sys.path.insert(0, parent)
        from schedule_manager_app.app import App as _App
        return _App

App = _load_app_class()

def main() -> None:
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
