"""toolbar.py — toolbar action callbacks (add_text, add_obj, new_document, on_preset, on_lang_change)."""
import dearpygui.dearpygui as dpg
import state
import draw
import panels
import history
import i18n


def add_text(s, u):
    state.st["add_mode"] = "text"
    state.set_status(i18n.t("status_draw_text"))


def add_obj(s, u):
    state.st["add_mode"] = "obj"
    state.set_status(i18n.t("status_draw_obj"))


def new_document(s, u):
    history.push_history()
    state.st["elements"].clear()
    state.st["selected"] = -1
    state.st["add_mode"] = None
    state.st["drag"] = None
    state.st["draw_start"] = None
    for tag in ["inp_high", "inp_style_aesthetics", "inp_style_lighting",
                "inp_style_art_style", "inp_style_medium", "inp_style_palette", "inp_bg"]:
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, "")
    panels.refresh_all()
    state.set_status(i18n.t("status_new"))


def on_preset(s, name):
    for p in state.PRESETS:
        if p["name"] == name:
            state.st["img_w"], state.st["img_h"] = p["w"], p["h"]
            break
    draw.redraw()


def on_lang_change(s, lang_name: str) -> None:
    i18n.set_lang(lang_name)
    import ui
    ui.refresh_ui_strings()
    panels.refresh_all()
    state.set_status(i18n.t("status_initial"))
