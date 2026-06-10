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
        "inp_high":             "A glamorous woman",
        "inp_style_aesthetics": "glossy editorial",
        "inp_style_lighting":   "dramatic",
        "inp_style_art_style":  "",
        "inp_style_medium":     "",
        "inp_style_palette":    "#CC0000, #FFFFFF",
        "inp_bg":               "gradient black",
    }.get(tag, "")

    state.st["elements"] = [
        {"type": "text", "bbox": [0, 0, 100, 200], "text": "HELLO", "desc": ""},
    ]
    result = prompt_io.build_prompt()

    assert result["high_level_description"] == "A glamorous woman"
    assert result["compositional_deconstruction"]["background"] == "gradient black"
    assert len(result["compositional_deconstruction"]["elements"]) == 1
    style = result["style_description"]
    assert isinstance(style, dict)
    assert style["aesthetics"] == "glossy editorial"
    assert style["lighting"] == "dramatic"
    assert "art_style" not in style  # empty fields omitted
    assert style["color_palette"] == ["#CC0000", "#FFFFFF"]


def test_build_prompt_style_empty_fields_omitted():
    import dearpygui.dearpygui as dpg
    dpg.get_value.side_effect = lambda tag: {
        "inp_high":             "",
        "inp_style_aesthetics": "",
        "inp_style_lighting":   "",
        "inp_style_art_style":  "",
        "inp_style_medium":     "",
        "inp_style_palette":    "",
        "inp_bg":               "",
    }.get(tag, "")

    state.st["elements"] = []
    result = prompt_io.build_prompt()
    assert result["style_description"] == {}


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

    real_open = open

    with patch("builtins.open", side_effect=lambda p, *a, **kw: real_open(p, *a, **kw)):
        with tempfile.TemporaryDirectory() as tmpdir:
            path_no_ext = os.path.join(tmpdir, "myprompt")
            # Old-style app_data (no current_path/file_name) → fallback branch
            app_data = {"selections": {path_no_ext: path_no_ext}, "file_path_name": path_no_ext}
            prompt_io.on_save_selected(None, app_data)
            assert os.path.exists(path_no_ext + ".json")


def test_on_save_dpg_filter_artifact_in_filename():
    """DPG embeds active filter pattern into file_name (e.g. 'prompt.*.*').
    _resolve_save_path must strip the artifact and produce a clean .json path."""
    import dearpygui.dearpygui as dpg
    dpg.get_value.side_effect = lambda tag: ""
    state.st["elements"] = []

    real_open = open

    with patch("builtins.open", side_effect=lambda p, *a, **kw: real_open(p, *a, **kw)):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Realistic DPG app_data with filter noise
            app_data = {
                "current_path": tmpdir,
                "file_name": "myprompt.*.*",
                "file_path_name": os.path.join(tmpdir, "myprompt.*.*"),
                "current_filter": ".*",
                "selections": {},
            }
            prompt_io.on_save_selected(None, app_data)
            assert os.path.exists(os.path.join(tmpdir, "myprompt.json"))


# ── _resolve_save_path ────────────────────────────────────────────────────────

def test_resolve_save_path_from_current_path_and_clean_name():
    app_data = {
        "current_path": "/tmp/prompts",
        "file_name": "myfile",
        "file_path_name": "",
        "selections": {},
    }
    assert prompt_io._resolve_save_path(app_data) == "/tmp/prompts/myfile.json"


def test_resolve_save_path_strips_filter_artifacts():
    app_data = {
        "current_path": "/tmp/prompts",
        "file_name": "myfile.*.*",
        "file_path_name": "/tmp/prompts/myfile.*.*",
        "current_filter": ".*",
        "selections": {},
    }
    assert prompt_io._resolve_save_path(app_data) == "/tmp/prompts/myfile.json"


def test_resolve_save_path_fallback_to_selections():
    app_data = {
        "selections": {"/tmp/x": "/tmp/x"},
        "file_path_name": "",
    }
    assert prompt_io._resolve_save_path(app_data) == "/tmp/x.json"


def test_resolve_save_path_empty_returns_empty():
    assert prompt_io._resolve_save_path({"selections": {}, "file_path_name": ""}) == ""


# ── round-trip: save → load ───────────────────────────────────────────────────

def _full_field_values():
    """Return a dpg.get_value side_effect covering all prompt fields."""
    return lambda tag: {
        "inp_high":             "A test scene",
        "inp_style_aesthetics": "cinematic",
        "inp_style_lighting":   "golden hour",
        "inp_style_art_style":  "realism",
        "inp_style_medium":     "oil painting",
        "inp_style_palette":    "#FF0000, #00FF00",
        "inp_bg":               "gradient sky",
    }.get(tag, "")


def test_roundtrip_save_then_load():
    """build_prompt() → write file → _parse_file() → _load_data() preserves all fields."""
    import dearpygui.dearpygui as dpg

    # ── Save phase ──
    dpg.get_value.side_effect = _full_field_values()
    state.st["elements"] = [
        {"type": "text", "bbox": [0, 0, 500, 500], "text": "HELLO", "desc": ""},
        {"type": "obj",  "bbox": [500, 500, 1000, 1000], "desc": "sky", "color_palette": []},
    ]
    prompt = prompt_io.build_prompt()

    with tempfile.NamedTemporaryFile(suffix=".json", mode="w",
                                     delete=False, encoding="utf-8") as f:
        json.dump(prompt, f, ensure_ascii=False, indent=2)
        saved_path = f.name

    try:
        # ── Load phase ──
        loaded = prompt_io._parse_file(saved_path)

        # Verify structure survived serialisation
        assert loaded["high_level_description"] == "A test scene"
        assert loaded["compositional_deconstruction"]["background"] == "gradient sky"

        style = loaded["style_description"]
        assert style["aesthetics"] == "cinematic"
        assert style["lighting"]   == "golden hour"
        assert style["art_style"]  == "realism"
        assert style["medium"]     == "oil painting"
        assert style["color_palette"] == ["#FF0000", "#00FF00"]

        elements = loaded["compositional_deconstruction"]["elements"]
        assert len(elements) == 2
        assert elements[0]["type"] == "text"
        assert elements[0]["text"] == "HELLO"
        assert elements[1]["type"] == "obj"

        # ── _load_data restores state ──
        set_calls: dict = {}
        dpg.set_value.side_effect = lambda tag, val: set_calls.update({tag: val})
        state.st["elements"] = []

        import panels
        with patch.object(panels, "refresh_all", lambda: None):
            prompt_io._load_data(loaded)

        assert set_calls["inp_high"]             == "A test scene"
        assert set_calls["inp_style_aesthetics"] == "cinematic"
        assert set_calls["inp_style_lighting"]   == "golden hour"
        assert set_calls["inp_style_art_style"]  == "realism"
        assert set_calls["inp_style_medium"]     == "oil painting"
        assert set_calls["inp_style_palette"]    == "#FF0000, #00FF00"
        assert set_calls["inp_bg"]               == "gradient sky"
        assert len(state.st["elements"]) == 2
        assert state.st["selected"] == -1

    finally:
        os.unlink(saved_path)


def test_roundtrip_empty_prompt():
    """Empty fields save and load without errors."""
    import dearpygui.dearpygui as dpg
    dpg.get_value.side_effect = lambda tag: ""
    state.st["elements"] = []
    prompt = prompt_io.build_prompt()

    with tempfile.NamedTemporaryFile(suffix=".json", mode="w",
                                     delete=False, encoding="utf-8") as f:
        json.dump(prompt, f)
        path = f.name
    try:
        loaded = prompt_io._parse_file(path)
        assert loaded["style_description"] == {}
        assert loaded["compositional_deconstruction"]["elements"] == []
    finally:
        os.unlink(path)


def test_load_legacy_string_style_goes_to_aesthetics():
    """Old JSON with style_description as plain string → loaded into aesthetics field."""
    import dearpygui.dearpygui as dpg
    data = {
        "high_level_description": "old prompt",
        "style_description": "vintage photography",
        "compositional_deconstruction": {"background": "", "elements": []},
    }
    set_calls: dict = {}
    dpg.set_value.side_effect = lambda tag, val: set_calls.update({tag: val})

    import panels
    with patch.object(panels, "refresh_all", lambda: None):
        prompt_io._load_data(data)

    assert set_calls["inp_style_aesthetics"] == "vintage photography"
    assert set_calls["inp_style_lighting"]   == ""
    assert set_calls["inp_style_art_style"]  == ""


def test_on_open_selected_missing_file_sets_status():
    captured = []
    with patch.object(state, "set_status", lambda m: captured.append(m)):
        prompt_io.on_open_selected(None, {"selections": {}, "file_path_name": "/nonexistent/file.json"})
    assert captured
    assert i18n.t("status_no_file") in captured[0]


def test_on_open_selected_loads_file():
    """on_open_selected reads a real file and populates state."""
    import dearpygui.dearpygui as dpg
    data = {
        "high_level_description": "open test",
        "style_description": {"aesthetics": "noir"},
        "compositional_deconstruction": {
            "background": "dark alley",
            "elements": [{"type": "obj", "bbox": [0, 0, 100, 100], "desc": "lamp"}],
        },
    }
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w",
                                     delete=False, encoding="utf-8") as f:
        json.dump(data, f)
        path = f.name
    try:
        set_calls: dict = {}
        dpg.set_value.side_effect = lambda tag, val: set_calls.update({tag: val})
        state.st["elements"] = []

        import panels, history
        with patch.object(panels, "refresh_all", lambda: None), \
             patch.object(history, "push_history", lambda: None):
            prompt_io.on_open_selected(None, {"selections": {path: path}, "file_path_name": ""})

        assert set_calls.get("inp_high") == "open test"
        assert set_calls.get("inp_style_aesthetics") == "noir"
        assert set_calls.get("inp_bg") == "dark alley"
        assert len(state.st["elements"]) == 1
        assert state.st["elements"][0]["desc"] == "lamp"
    finally:
        os.unlink(path)


def test_confirm_overwrite_saves_pending_path():
    """confirm_overwrite() writes _pending_save_path to disk."""
    import dearpygui.dearpygui as dpg
    dpg.get_value.side_effect = lambda tag: ""
    dpg.configure_item.return_value = None
    state.st["elements"] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        target = os.path.join(tmpdir, "existing.json")
        open(target, "w").close()  # create so isfile=True

        prompt_io._pending_save_path = target
        prompt_io.confirm_overwrite()
        assert os.path.exists(target)
        content = json.loads(open(target).read())
        assert "high_level_description" in content


def test_on_save_no_path_sets_status():
    captured = []
    with patch.object(state, "set_status", lambda m: captured.append(m)):
        prompt_io.on_save_selected(None, {"selections": {}, "file_path_name": ""})
    assert captured
    assert i18n.t("status_no_path") in captured[0]


# ── open_file (native dialog entrypoint) ───────────────────────────────────────

def test_open_file_missing_sets_status():
    captured = []
    with patch.object(state, "set_status", lambda m: captured.append(m)):
        prompt_io.open_file("/nonexistent/file.json")
    assert captured
    assert i18n.t("status_no_file") in captured[0]


def test_open_file_loads_file():
    import dearpygui.dearpygui as dpg
    data = {
        "high_level_description": "native open test",
        "style_description": {"aesthetics": "brutalism"},
        "compositional_deconstruction": {
            "background": "concrete",
            "elements": [{"type": "obj", "bbox": [0, 0, 500, 500], "desc": "pillar"}],
        },
    }
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w",
                                     delete=False, encoding="utf-8") as f:
        json.dump(data, f)
        path = f.name
    try:
        set_calls: dict = {}
        dpg.set_value.side_effect = lambda tag, val: set_calls.update({tag: val})
        state.st["elements"] = []

        import panels, history
        with patch.object(panels, "refresh_all", lambda: None), \
             patch.object(history, "push_history", lambda: None):
            prompt_io.open_file(path)

        assert set_calls.get("inp_high") == "native open test"
        assert set_calls.get("inp_style_aesthetics") == "brutalism"
        assert len(state.st["elements"]) == 1
        assert state.st["elements"][0]["desc"] == "pillar"
    finally:
        os.unlink(path)


# ── save_file (native dialog entrypoint) ───────────────────────────────────────

def test_save_file_empty_path_sets_status():
    captured = []
    with patch.object(state, "set_status", lambda m: captured.append(m)):
        prompt_io.save_file("")
    assert captured
    assert i18n.t("status_no_path") in captured[0]


def test_save_file_appends_json_extension():
    import dearpygui.dearpygui as dpg
    dpg.get_value.side_effect = lambda tag: ""
    state.st["elements"] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        target = os.path.join(tmpdir, "myfile")
        prompt_io.save_file(target)
        assert os.path.exists(target + ".json")


def test_save_file_writes_json():
    import dearpygui.dearpygui as dpg
    dpg.get_value.side_effect = lambda tag: ""
    state.st["elements"] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        target = os.path.join(tmpdir, "out.json")
        prompt_io.save_file(target)
        content = json.loads(open(target).read())
        assert "high_level_description" in content
