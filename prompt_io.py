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
    style = data.get("style_description", "")
    dpg.set_value(
        "inp_style",
        json.dumps(style, ensure_ascii=False, indent=2)
        if isinstance(style, dict) else str(style),
    )
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
    style_raw = dpg.get_value("inp_style").strip()
    try:
        style_val = json.loads(style_raw)
    except Exception:
        style_val = style_raw
    return {
        "high_level_description": dpg.get_value("inp_high"),
        "style_description": style_val,
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
        history.push_history()
        _load_data(_parse_file(path))
        state.set_status(i18n.t("status_opened", name=os.path.basename(path), count=len(state.st["elements"])))
    except Exception as e:
        state.set_status(i18n.t("status_error_open", err=e))


def on_save_selected(sender, app_data):
    selections = app_data.get("selections", {})
    path = next(iter(selections.values())) if selections else app_data.get("file_path_name", "")
    if not path:
        state.set_status(i18n.t("status_no_path"))
        return
    if not path.endswith(".json"):
        path += ".json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(build_prompt(), f, ensure_ascii=False, indent=2)
        state.set_status(i18n.t("status_saved", path=path))
    except Exception as e:
        state.set_status(i18n.t("status_error_save", err=e))
