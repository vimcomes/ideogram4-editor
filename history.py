"""history.py — undo history management."""
import json
import state
import i18n

_history: list = []
MAX_HISTORY = 60


def push_history() -> None:
    _history.append(json.loads(json.dumps(state.st["elements"])))
    if len(_history) > MAX_HISTORY:
        _history.pop(0)


def undo() -> None:
    import panels  # late import to avoid circular dependency
    if not _history:
        state.set_status(i18n.t("status_undo_empty"))
        return
    state.st["elements"] = _history.pop()
    state.st["selected"] = min(state.st["selected"], len(state.st["elements"]) - 1)
    panels.refresh_all()
    state.set_status(i18n.t("status_undo_done", count=len(_history)))


def clear() -> None:
    _history.clear()
