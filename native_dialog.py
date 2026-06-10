"""native_dialog.py — native OS file dialogs via tkinter, with DPG fallback.

Tkinter dialogs are blocking, so each call spawns a daemon thread.
Callbacks are posted to _pending and drained on the main thread via flush(),
which is called from the render loop — safe for DPG operations.
"""
import threading

_pending: list = []


def flush() -> None:
    """Drain posted callbacks. Call from the render loop (main thread)."""
    while _pending:
        _pending.pop(0)()


def _post(fn) -> None:
    _pending.append(fn)


def open_file(title: str, filetypes: list, initial_dir: str,
              on_done, fallback_tag: str = "") -> None:
    """Open a native file-open dialog in a background thread.

    on_done(path: str) is called on the main thread after user confirms.
    Falls back to DPG dialog (fallback_tag) when tkinter is unavailable.
    """
    def _run():
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            path = filedialog.askopenfilename(
                title=title,
                filetypes=filetypes,
                initialdir=initial_dir,
            )
            root.destroy()
            if path:
                _post(lambda p=path: on_done(p))
        except ImportError:
            if fallback_tag:
                import dearpygui.dearpygui as dpg
                _post(lambda: dpg.show_item(fallback_tag))

    threading.Thread(target=_run, daemon=True).start()


def save_file(title: str, filetypes: list, initial_dir: str,
              default_ext: str, default_name: str,
              on_done, fallback_tag: str = "") -> None:
    """Open a native file-save dialog in a background thread."""
    def _run():
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            path = filedialog.asksaveasfilename(
                title=title,
                filetypes=filetypes,
                initialdir=initial_dir,
                defaultextension=default_ext,
                initialfile=default_name,
            )
            root.destroy()
            if path:
                _post(lambda p=path: on_done(p))
        except ImportError:
            if fallback_tag:
                import dearpygui.dearpygui as dpg
                _post(lambda: dpg.show_item(fallback_tag))

    threading.Thread(target=_run, daemon=True).start()
