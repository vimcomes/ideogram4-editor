"""ui.py — builds the DPG window, dialogs, and three-column table layout."""
import dearpygui.dearpygui as dpg
import state
import config
import handlers
import prompt_io
import i18n


def _open_file(s, u):
    if dpg.does_item_exist("open_dlg"):
        dpg.show_item("open_dlg")


def _save_file(s, u):
    if dpg.does_item_exist("save_dlg"):
        dpg.show_item("save_dlg")


def refresh_ui_strings() -> None:
    """Update all tagged static UI items to the current language."""
    mapping = {
        # (tag, setter): value
        # dpg.set_value for text widgets, dpg.set_item_label for buttons/combos
    }
    # Text widgets (add_text uses set_value)
    text_tags = {
        "ui_text_resolution":   "toolbar_resolution",
        "ui_text_layers_title": "panel_layers_title",
        "ui_text_props_title":  "panel_props_title",
        "ui_text_high_label":   "field_high_level",
        "ui_text_style_label":  "field_style",
        "ui_text_bg_label":     "field_background",
    }
    for tag, key in text_tags.items():
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, i18n.t(key))

    # Button/item labels (set_item_label)
    label_tags = {
        "btn_copy":      "toolbar_btn_copy",
        "btn_open":      "toolbar_btn_open",
        "btn_save":      "toolbar_btn_save",
        "btn_undo":      "toolbar_btn_undo",
        "btn_add_text":  "toolbar_btn_add_text",
        "btn_add_obj":   "toolbar_btn_add_obj",
        "btn_move_up":   "toolbar_btn_move_up",
        "btn_move_down": "toolbar_btn_move_down",
        "btn_delete":    "toolbar_btn_delete",
    }
    for tag, key in label_tags.items():
        if dpg.does_item_exist(tag):
            dpg.set_item_label(tag, i18n.t(key))

    # Status bar hint
    if dpg.does_item_exist("status_bar"):
        dpg.set_value("status_bar", i18n.t("status_initial"))


def build_ui() -> None:
    # ── File dialogs ──────────────────────────────────────────────────────────
    with dpg.file_dialog(
        tag="open_dlg",
        label=i18n.t("dialog_open_title"),
        callback=prompt_io.on_open_selected,
        cancel_callback=lambda s, a: None,
        default_path=config.PROMPTS_DIR,
        width=700, height=440,
        show=False, modal=True,
    ):
        dpg.add_file_extension(".*",    color=(200, 200, 200, 255), custom_text=i18n.t("file_filter_all"))
        dpg.add_file_extension(".json", color=(100, 220, 100, 255), custom_text=i18n.t("file_filter_json"))
        dpg.add_file_extension(".txt",  color=(220, 200, 80, 255),  custom_text=i18n.t("file_filter_txt"))

    with dpg.file_dialog(
        tag="save_dlg",
        label=i18n.t("dialog_save_title"),
        callback=prompt_io.on_save_selected,
        cancel_callback=lambda s, a: None,
        default_path=config.PROMPTS_DIR,
        default_filename="prompt.json",
        width=700, height=440,
        show=False, modal=True,
    ):
        dpg.add_file_extension(".*",    color=(200, 200, 200, 255), custom_text=i18n.t("file_filter_all"))
        dpg.add_file_extension(".json", color=(100, 220, 100, 255), custom_text=i18n.t("file_filter_json"))

    # ── Main window ───────────────────────────────────────────────────────────
    with dpg.window(
        tag="main",
        label="Ideogram4 Layout Editor",
        width=config.INIT_W, height=config.INIT_H,
        no_resize=False, no_move=False, no_title_bar=True,
        no_scrollbar=True, no_scroll_with_mouse=True,
    ):
        # ── Toolbar ───────────────────────────────────────────────────────────
        with dpg.group(horizontal=True):
            dpg.add_text(i18n.t("toolbar_resolution"), tag="ui_text_resolution")
            dpg.add_combo(
                state.PRESET_NAMES,
                default_value=state.PRESET_NAMES[3],
                width=185,
                callback=handlers.on_preset,
            )
            dpg.add_button(tag="btn_copy",  label=i18n.t("toolbar_btn_copy"),  callback=prompt_io.copy_to_clipboard)
            dpg.add_button(tag="btn_open",  label=i18n.t("toolbar_btn_open"),  callback=_open_file)
            dpg.add_button(tag="btn_save",  label=i18n.t("toolbar_btn_save"),  callback=_save_file)
            dpg.add_button(tag="btn_undo",  label=i18n.t("toolbar_btn_undo"),  callback=lambda s, u: __import__("history").undo())
            dpg.add_separator()
            dpg.add_text("Lang:")
            dpg.add_combo(
                i18n.AVAILABLE_LANGS,
                default_value=i18n.get_lang(),
                width=55,
                callback=handlers.on_lang_change,
            )

        dpg.add_separator()

        # ── Three-panel table ─────────────────────────────────────────────────
        with dpg.table(
            tag="main_table",
            resizable=True, borders_innerV=True,
            header_row=False,
            width=-1, height=-1,
            policy=dpg.mvTable_SizingStretchProp,
        ):
            dpg.add_table_column(tag="col_left",  init_width_or_weight=0.17, width_stretch=True)
            dpg.add_table_column(tag="col_mid",   init_width_or_weight=0.50, width_stretch=True)
            dpg.add_table_column(tag="col_right", init_width_or_weight=0.33, width_stretch=True)

            with dpg.table_row():

                # ── LEFT: layer panel ─────────────────────────────────────────
                with dpg.table_cell():
                    with dpg.child_window(tag="panel_left", width=-1, height=-1, border=True):
                        dpg.add_text(i18n.t("panel_layers_title"), tag="ui_text_layers_title", color=(200, 200, 100, 255))
                        dpg.add_separator()
                        with dpg.group(horizontal=True):
                            dpg.add_button(tag="btn_add_text", label=i18n.t("toolbar_btn_add_text"), width=55, callback=handlers.add_text)
                            dpg.add_button(tag="btn_add_obj",  label=i18n.t("toolbar_btn_add_obj"),  width=55, callback=handlers.add_obj)
                        dpg.add_separator()

                        with dpg.child_window(tag="layer_list", width=-1, height=-1, border=False):
                            pass

                        dpg.add_separator()
                        dpg.add_button(tag="btn_move_up",   label=i18n.t("toolbar_btn_move_up"),   width=-1, callback=handlers.move_up)
                        dpg.add_button(tag="btn_move_down", label=i18n.t("toolbar_btn_move_down"), width=-1, callback=handlers.move_down)
                        dpg.add_button(tag="btn_delete",    label=i18n.t("toolbar_btn_delete"),    width=-1, callback=handlers.del_selected)

                # ── MIDDLE: canvas + global fields ────────────────────────────
                with dpg.table_cell():
                    with dpg.child_window(
                        tag="panel_mid",
                        width=-1, height=-1,
                        border=False, no_scrollbar=True,
                    ):
                        # canvas_dl starts small; render loop updates its size
                        dpg.add_drawlist(tag="canvas_dl", width=400, height=10)
                        dpg.add_separator()
                        with dpg.child_window(
                            tag="fields_panel",
                            width=-1, height=215,
                            border=False, no_scrollbar=True,
                        ):
                            dpg.add_text(i18n.t("field_high_level"), tag="ui_text_high_label")
                            dpg.add_input_text(
                                tag="inp_high", width=-1,
                                multiline=True, height=48, default_value="",
                            )
                            dpg.add_text(i18n.t("field_style"), tag="ui_text_style_label")
                            dpg.add_input_text(
                                tag="inp_style", width=-1,
                                multiline=True, height=42, default_value="",
                            )
                            dpg.add_text(i18n.t("field_background"), tag="ui_text_bg_label")
                            dpg.add_input_text(tag="inp_bg", width=-1, default_value="")

                # ── RIGHT: properties ─────────────────────────────────────────
                with dpg.table_cell():
                    with dpg.child_window(tag="panel_right", width=-1, height=-1, border=True):
                        dpg.add_text(i18n.t("panel_props_title"), tag="ui_text_props_title", color=(200, 200, 100, 255))
                        dpg.add_separator()
                        with dpg.child_window(
                            tag="props_group",
                            width=-1, height=-1,
                            border=False,
                        ):
                            dpg.add_text(i18n.t("props_no_selection"), color=(160, 160, 160, 255))

        dpg.add_separator()
        dpg.add_text(
            tag="status_bar",
            default_value=i18n.t("status_initial"),
        )
