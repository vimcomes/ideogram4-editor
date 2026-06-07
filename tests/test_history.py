"""Tests for history (undo) module."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, patch
sys.modules["dearpygui"] = MagicMock()
sys.modules["dearpygui.dearpygui"] = MagicMock()

import state
import history
import i18n


def _reset():
    history.clear()
    state.st["elements"] = []
    state.st["selected"] = -1
    i18n.set_lang("ru")


def test_push_history_stores_snapshot():
    _reset()
    state.st["elements"] = [{"type": "text", "bbox": [0, 0, 100, 100]}]
    history.push_history()
    assert len(history._history) == 1


def test_push_history_deep_copy():
    _reset()
    el = {"type": "text", "bbox": [0, 0, 100, 100]}
    state.st["elements"] = [el]
    history.push_history()
    # Mutate original — snapshot must not change
    el["bbox"][0] = 999
    assert history._history[0][0]["bbox"][0] == 0


def test_push_history_max_limit():
    _reset()
    for _ in range(history.MAX_HISTORY + 10):
        state.st["elements"] = [{"type": "obj", "bbox": [0, 0, 10, 10]}]
        history.push_history()
    assert len(history._history) <= history.MAX_HISTORY


def test_undo_restores_elements():
    _reset()
    state.st["elements"] = [{"type": "obj", "bbox": [0, 0, 500, 500]}]
    history.push_history()
    state.st["elements"] = []  # simulate deletion

    with patch("panels.refresh_all"):
        history.undo()

    assert len(state.st["elements"]) == 1
    assert state.st["elements"][0]["bbox"] == [0, 0, 500, 500]


def test_undo_empty_sets_status():
    _reset()
    captured = []

    def fake_set_status(msg):
        captured.append(msg)

    with patch.object(state, "set_status", fake_set_status):
        history.undo()

    assert captured
    assert i18n.t("status_undo_empty") in captured[0]


def test_undo_adjusts_selected_when_out_of_bounds():
    _reset()
    state.st["elements"] = [
        {"type": "obj", "bbox": [0, 0, 100, 100]},
    ]
    state.st["selected"] = 0
    history.push_history()
    state.st["elements"] = []
    state.st["selected"] = 5  # invalid after deletion

    with patch("panels.refresh_all"):
        history.undo()

    assert state.st["selected"] <= len(state.st["elements"])


def test_undo_status_contains_count():
    _reset()
    state.st["elements"] = [{"type": "obj", "bbox": [0, 0, 100, 100]}]
    history.push_history()
    history.push_history()
    state.st["elements"] = []

    captured = []
    with patch.object(state, "set_status", lambda m: captured.append(m)):
        with patch("panels.refresh_all"):
            history.undo()

    # After undo, one snapshot consumed; history has 1 left
    assert "1" in captured[-1]


def test_clear_empties_history():
    _reset()
    state.st["elements"] = [{"type": "text", "bbox": [0, 0, 50, 50]}]
    history.push_history()
    history.push_history()
    history.clear()
    assert history._history == []
