"""Tests for prompt_io — pure logic (parse/build), no DPG required."""
import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, patch
sys.modules["dearpygui"] = MagicMock()
sys.modules["dearpygui.dearpygui"] = MagicMock()

import i18n
import state
import prompt_io


def _make_prompt_dict(elements=None):
    return {
        "high_level_description": "A test prompt",
        "style_description": {"key": "val"},
        "compositional_deconstruction": {
            "background": "white",
            "elements": elements or [],
        },
    }


# ── _parse_file ────────────────────────────────────────────────────────────────

def test_parse_json_file():
    data = _make_prompt_dict()
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False, encoding="utf-8") as f:
        json.dump(data, f)
        path = f.name
    try:
        result = prompt_io._parse_file(path)
        assert result["high_level_description"] == "A test prompt"
    finally:
        os.unlink(path)


def test_parse_txt_file_with_embedded_json():
    data = _make_prompt_dict()
    txt_content = "Some preamble text\n" + json.dumps(data)
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False, encoding="utf-8") as f:
        f.write(txt_content)
        path = f.name
    try:
        result = prompt_io._parse_file(path)
        assert result["high_level_description"] == "A test prompt"
    finally:
        os.unlink(path)


def test_parse_txt_file_no_json_raises():
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False, encoding="utf-8") as f:
        f.write("No JSON here at all")
        path = f.name
    try:
        raised = False
        try:
            prompt_io._parse_file(path)
        except ValueError as e:
            raised = True
            assert i18n.t("error_json_not_in_txt") in str(e)
        assert raised
    finally:
        os.unlink(path)


def test_parse_invalid_json_raises():
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False, encoding="utf-8") as f:
        f.write("{bad json}")
        path = f.name
    try:
        raised = False
        try:
            prompt_io._parse_file(path)
        except json.JSONDecodeError:
            raised = True
        assert raised
    finally:
        os.unlink(path)


# ── build_prompt ───────────────────────────────────────────────────────────────

def test_build_prompt_structure():
    import dearpygui.dearpygui as dpg
    dpg.get_value.side_effect = lambda tag: {
        "inp_high": "A glamorous woman",
        "inp_style": '{"lighting": "dramatic"}',
        "inp_bg": "gradient black",
    }.get(tag, "")

    state.st["elements"] = [
        {"type": "text", "bbox": [0, 0, 100, 200], "text": "HELLO", "desc": ""},
    ]
    result = prompt_io.build_prompt()

    assert result["high_level_description"] == "A glamorous woman"
    assert result["compositional_deconstruction"]["background"] == "gradient black"
    assert len(result["compositional_deconstruction"]["elements"]) == 1


def test_build_prompt_invalid_style_json_kept_as_string():
    import dearpygui.dearpygui as dpg
    dpg.get_value.side_effect = lambda tag: {
        "inp_high": "",
        "inp_style": "not valid json {{{",
        "inp_bg": "",
    }.get(tag, "")

    state.st["elements"] = []
    result = prompt_io.build_prompt()
    assert isinstance(result["style_description"], str)


def test_build_prompt_elements_are_copies():
    import dearpygui.dearpygui as dpg
    dpg.get_value.side_effect = lambda tag: ""
    original = {"type": "obj", "bbox": [0, 0, 500, 500], "desc": "test"}
    state.st["elements"] = [original]

    result = prompt_io.build_prompt()
    result["compositional_deconstruction"]["elements"][0]["desc"] = "mutated"
    assert original["desc"] == "test"  # shallow copy — desc not mutated via list item


# ── on_save_selected ───────────────────────────────────────────────────────────

def test_on_save_adds_json_extension():
    import dearpygui.dearpygui as dpg
    dpg.get_value.side_effect = lambda tag: ""
    state.st["elements"] = []

    saved_paths = []
    real_open = open

    with patch("builtins.open", side_effect=lambda p, *a, **kw: real_open(p, *a, **kw)) as mock_open:
        with tempfile.TemporaryDirectory() as tmpdir:
            path_no_ext = os.path.join(tmpdir, "myprompt")
            app_data = {"selections": {path_no_ext: path_no_ext}, "file_path_name": path_no_ext}
            prompt_io.on_save_selected(None, app_data)
            expected = path_no_ext + ".json"
            assert os.path.exists(expected)


def test_on_save_no_path_sets_status():
    captured = []
    with patch.object(state, "set_status", lambda m: captured.append(m)):
        prompt_io.on_save_selected(None, {"selections": {}, "file_path_name": ""})
    assert captured
    assert i18n.t("status_no_path") in captured[0]
