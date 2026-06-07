"""history.py — undo history management."""
import json
import state

_history: list = []
MAX_HISTORY = 60


def push_history() -> None:
    _history.append(json.loads(json.dumps(state.st["elements"])))
    if len(_history) > MAX_HISTORY:
        _history.pop(0)


def undo() -> None:
    import panels  # late import to avoid circular dependency
    if not _history:
        state.set_status("Нечего отменять.")
        return
    state.st["elements"] = _history.pop()
    state.st["selected"] = min(state.st["selected"], len(state.st["elements"]) - 1)
    panels.refresh_all()
    state.set_status(f"Undo  ({len(_history)} шагов в истории)")
