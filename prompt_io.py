"""prompt_io.py — file open/save and clipboard export for prompts."""
import json
import os
import dearpygui.dearpygui as dpg
import state
import panels
import i18n


def _parse_file(path: str) -> dict:
    raw = open(path, encoding="utf-8").read()
    if path.endswith(".txt"):
        start = raw.find("{")
        if start == -1:
            raise ValueError(i18n.t("error_json_not_in_txt"))
        raw = raw[start:]
    return json.loads(raw)


def _load_data(data: dict) -> None:
    dpg.set_value("inp_high", data.get("high_level_description", ""))

    style = data.get("style_description", {})
    if isinstance(style, dict):
        dpg.set_value("inp_style_aesthetics", style.get("aesthetics", ""))
        dpg.set_value("inp_style_lighting",   style.get("lighting", ""))
        dpg.set_value("inp_style_medium",     style.get("medium", ""))
        palette = style.get("color_palette", [])
        dpg.set_value("inp_style_palette",
                      ", ".join(palette) if isinstance(palette, list) else str(palette))
        # Detect photo vs art mode from loaded JSON
        import toolbar as _tb
        if "photo" in style:
            dpg.set_value("inp_style_photo",     style.get("photo", ""))
            dpg.set_value("inp_style_art_style", "")
            if dpg.does_item_exist("style_mode_radio"):
                dpg.set_value("style_mode_radio", "photo")
            _tb.on_style_mode_change(None, "photo")
        else:
            dpg.set_value("inp_style_art_style", style.get("art_style", ""))
            dpg.set_value("inp_style_photo",     "")
            if dpg.does_item_exist("style_mode_radio"):
                dpg.set_value("style_mode_radio", "art")
            _tb.on_style_mode_change(None, "art")
    else:
        # Fallback: plain string → put in aesthetics
        import toolbar as _tb
        dpg.set_value("inp_style_aesthetics", str(style) if style else "")
        dpg.set_value("inp_style_lighting",   "")
        dpg.set_value("inp_style_photo",      "")
        dpg.set_value("inp_style_art_style",  "")
        dpg.set_value("inp_style_medium",     "")
        dpg.set_value("inp_style_palette",    "")
        if dpg.does_item_exist("style_mode_radio"):
            dpg.set_value("style_mode_radio", "art")
        _tb.on_style_mode_change(None, "art")

    dpg.set_value(
        "inp_bg",
        data.get("compositional_deconstruction", {}).get("background", ""),
    )
    state.st["elements"] = list(
        data.get("compositional_deconstruction", {}).get("elements", [])
    )
    state.st["selected"] = -1
    panels.refresh_all()


def build_prompt() -> dict:
    style: dict = {}
    # Always first: aesthetics, lighting
    for key, tag in [
        ("aesthetics", "inp_style_aesthetics"),
        ("lighting",   "inp_style_lighting"),
    ]:
        val = dpg.get_value(tag).strip()
        if val:
            style[key] = val
    # Key order depends on mode (matches Ideogram 4 training schema)
    if state.g_style_mode == "photo":
        # photo → medium
        for key, tag in [("photo", "inp_style_photo"), ("medium", "inp_style_medium")]:
            val = dpg.get_value(tag).strip()
            if val:
                style[key] = val
    else:
        # medium → art_style
        for key, tag in [("medium", "inp_style_medium"), ("art_style", "inp_style_art_style")]:
            val = dpg.get_value(tag).strip()
            if val:
                style[key] = val
    palette_raw = dpg.get_value("inp_style_palette").strip()
    if palette_raw:
        style["color_palette"] = [c.strip() for c in palette_raw.split(",") if c.strip()]

    return {
        "high_level_description": dpg.get_value("inp_high"),
        "style_description": style,
        "compositional_deconstruction": {
            "background": dpg.get_value("inp_bg"),
            "elements": [dict(el) for el in state.st["elements"]],
        },
    }


def copy_to_clipboard(s, u):
    try:
        text = json.dumps(build_prompt(), ensure_ascii=False, indent=2)
        dpg.set_clipboard_text(text)
        state.set_status(i18n.t("status_copied", count=len(state.st["elements"])))
    except Exception as e:
        state.set_status(i18n.t("status_error", err=e))


def on_open_selected(sender, app_data):
    import history  # avoid top-level circular; history ← state only
    selections = app_data.get("selections", {})
    path = next(iter(selections.values())) if selections else app_data.get("file_path_name", "")
    if not path or not os.path.isfile(path):
        state.set_status(i18n.t("status_no_file"))
        return
    try:
        history.clear()
        _load_data(_parse_file(path))
        state.set_status(i18n.t("status_opened", name=os.path.basename(path), count=len(state.st["elements"])))
    except Exception as e:
        state.set_status(i18n.t("status_error_open", err=e))


_pending_save_path: str = ""


def _do_save(path: str) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(build_prompt(), f, ensure_ascii=False, indent=2)
        state.set_status(i18n.t("status_saved", path=path))
    except Exception as e:
        state.set_status(i18n.t("status_error_save", err=e))


def confirm_overwrite() -> None:
    """Called by the Yes button in the pre-built overwrite dialog."""
    dpg.hide_item("overwrite_dlg")
    _do_save(_pending_save_path)


def _show_overwrite_confirm(path: str) -> None:
    global _pending_save_path
    _pending_save_path = path
    dpg.set_value("overwrite_dlg_text", i18n.t("dialog_overwrite_msg", name=os.path.basename(path)))
    vw, vh = dpg.get_viewport_width(), dpg.get_viewport_height()
    dpg.set_item_pos("overwrite_dlg", [vw // 2 - 170, vh // 2 - 57])
    dpg.show_item("overwrite_dlg")


def _resolve_save_path(app_data: dict) -> str:
    """Extract and clean the save path from file_dialog app_data.

    DPG embeds the active filter pattern into file_name (e.g. 'prompt.*.*').
    When current_path + file_name are present we clean the filter noise;
    otherwise fall back to selections / file_path_name (e.g. in tests).
    """
    import re
    current_path = app_data.get("current_path", "")
    file_name    = app_data.get("file_name", "")

    if current_path and file_name:
        # Strip filter artifacts: everything from the first '*' onward + trailing dots
        stem = re.sub(r"\*.*", "", file_name).rstrip(".")
        if stem:
            name = stem if stem.endswith(".json") else stem + ".json"
            return os.path.join(current_path, name)

    # Fallback: selections dict or raw file_path_name (no filter artifacts)
    selections = app_data.get("selections", {})
    path = next(iter(selections.values())) if selections else app_data.get("file_path_name", "")
    if not path:
        return ""
    if not path.endswith(".json"):
        path += ".json"
    return path


def on_save_selected(sender, app_data):
    path = _resolve_save_path(app_data)
    if not path:
        state.set_status(i18n.t("status_no_path"))
        return
    if os.path.isfile(path):
        _show_overwrite_confirm(path)
    else:
        _do_save(path)
