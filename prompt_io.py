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
        dpg.set_value("inp_style_art_style",  style.get("art_style", ""))
        dpg.set_value("inp_style_medium",     style.get("medium", ""))
        palette = style.get("color_palette", [])
        dpg.set_value("inp_style_palette",
                      ", ".join(palette) if isinstance(palette, list) else str(palette))
    else:
        # Fallback: plain string → put in aesthetics
        dpg.set_value("inp_style_aesthetics", str(style) if style else "")
        dpg.set_value("inp_style_lighting",   "")
        dpg.set_value("inp_style_art_style",  "")
        dpg.set_value("inp_style_medium",     "")
        dpg.set_value("inp_style_palette",    "")

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
    for key, tag in [
        ("aesthetics", "inp_style_aesthetics"),
        ("lighting",   "inp_style_lighting"),
        ("art_style",  "inp_style_art_style"),
        ("medium",     "inp_style_medium"),
    ]:
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
        history.push_history()
        _load_data(_parse_file(path))
        state.set_status(i18n.t("status_opened", name=os.path.basename(path), count=len(state.st["elements"])))
    except Exception as e:
        state.set_status(i18n.t("status_error_open", err=e))


def _do_save(path: str) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(build_prompt(), f, ensure_ascii=False, indent=2)
        state.set_status(i18n.t("status_saved", path=path))
    except Exception as e:
        state.set_status(i18n.t("status_error_save", err=e))


def _show_overwrite_confirm(path: str) -> None:
    tag = "overwrite_dlg"
    if dpg.does_item_exist(tag):
        dpg.delete_item(tag)
    vw = dpg.get_viewport_width()
    vh = dpg.get_viewport_height()
    with dpg.window(
        tag=tag, modal=True, no_close=True,
        label=i18n.t("dialog_overwrite_title"),
        width=320, height=110,
        pos=(vw // 2 - 160, vh // 2 - 55),
    ):
        dpg.add_text(i18n.t("dialog_overwrite_msg", name=os.path.basename(path)))
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(
                label=i18n.t("dialog_overwrite_yes"), width=100,
                callback=lambda s, u: (dpg.delete_item(tag), _do_save(path)),
            )
            dpg.add_button(
                label=i18n.t("dialog_overwrite_no"), width=100,
                callback=lambda s, u: dpg.delete_item(tag),
            )


def on_save_selected(sender, app_data):
    selections = app_data.get("selections", {})
    path = next(iter(selections.values())) if selections else app_data.get("file_path_name", "")
    if not path:
        state.set_status(i18n.t("status_no_path"))
        return
    if not path.endswith(".json"):
        path += ".json"
    if os.path.isfile(path):
        _show_overwrite_confirm(path)
    else:
        _do_save(path)
