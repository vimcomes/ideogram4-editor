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
    text_tags = {
        "ui_text_resolution":          "toolbar_resolution",
        "ui_text_layers_title":        "panel_layers_title",
        "ui_text_props_title":         "panel_props_title",
        "ui_text_high_label":          "field_high_level",
        "ui_text_style_aesthetics":    "field_style_aesthetics",
        "ui_text_style_lighting":      "field_style_lighting",
        "ui_text_style_art_style":     "field_style_art_style",
        "ui_text_style_medium":        "field_style_medium",
        "ui_text_style_palette":       "field_style_palette",
        "ui_text_bg_label":            "field_background",
    }
    for tag, key in text_tags.items():
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, i18n.t(key))

    label_tags = {
        "btn_new":         "toolbar_btn_new",
        "btn_copy":        "toolbar_btn_copy",
        "btn_open":        "toolbar_btn_open",
        "btn_save":        "toolbar_btn_save",
        "btn_undo":        "toolbar_btn_undo",
        "btn_add_text":    "toolbar_btn_add_text",
        "btn_add_obj":     "toolbar_btn_add_obj",
        "ui_style_header": "field_style",
    }
    for tag, key in label_tags.items():
        if dpg.does_item_exist(tag):
            dpg.set_item_label(tag, i18n.t(key))

    if dpg.does_item_exist("status_bar"):
        dpg.set_value("status_bar", i18n.t("status_initial"))


def _tooltip(parent, text: str) -> None:
    with dpg.tooltip(parent):
        dpg.add_text(text)


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
        # ── Toolbar (fixed child_window — never scrolls away) ─────────────────
        with dpg.child_window(
            tag="toolbar_panel",
            height=36,
            border=False,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        ):
            with dpg.group(horizontal=True):
                dpg.add_text(i18n.t("toolbar_resolution"), tag="ui_text_resolution")
                dpg.add_combo(
                    state.PRESET_NAMES,
                    default_value=state.PRESET_NAMES[3],
                    width=185,
                    callback=handlers.on_preset,
                )
                dpg.add_separator()

                btn_new = dpg.add_button(tag="btn_new",  label=i18n.t("toolbar_btn_new"),  callback=handlers.new_document)
                _tooltip(btn_new,  "New document (clear all)")
                btn_undo = dpg.add_button(tag="btn_undo", label=i18n.t("toolbar_btn_undo"), callback=lambda s, u: __import__("history").undo())
                _tooltip(btn_undo, "Undo (Ctrl+Z)")
                btn_copy = dpg.add_button(tag="btn_copy", label=i18n.t("toolbar_btn_copy"), callback=prompt_io.copy_to_clipboard)
                _tooltip(btn_copy, "Copy JSON to clipboard")
                btn_open = dpg.add_button(tag="btn_open", label=i18n.t("toolbar_btn_open"), callback=_open_file)
                _tooltip(btn_open, "Open prompt file")
                btn_save = dpg.add_button(tag="btn_save", label=i18n.t("toolbar_btn_save"), callback=_save_file)
                _tooltip(btn_save, "Save prompt")

                dpg.add_separator()
                dpg.add_text("Lang:")
                dpg.add_combo(
                    i18n.AVAILABLE_LANGS,
                    default_value=i18n.get_lang(),
                    width=55,
                    callback=handlers.on_lang_change,
                )

        dpg.add_separator()

        # ── Content area (fills viewport minus status bar) ────────────────────
        with dpg.child_window(
            tag="content_area",
            height=-26,
            border=False,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        ):
            # ── Three-panel table ─────────────────────────────────────────────
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

                    # ── LEFT: layer panel ─────────────────────────────────────
                    with dpg.table_cell():
                        with dpg.child_window(tag="panel_left", width=-1, height=-1, border=True):
                            dpg.add_text(i18n.t("panel_layers_title"), tag="ui_text_layers_title", color=(200, 200, 100, 255))
                            dpg.add_separator()
                            with dpg.group(horizontal=True):
                                btn_at = dpg.add_button(tag="btn_add_text", label=i18n.t("toolbar_btn_add_text"), width=32, callback=handlers.add_text)
                                _tooltip(btn_at, "Add text layer")
                                btn_ao = dpg.add_button(tag="btn_add_obj",  label=i18n.t("toolbar_btn_add_obj"),  width=32, callback=handlers.add_obj)
                                _tooltip(btn_ao, "Add object layer")
                            dpg.add_separator()

                            with dpg.child_window(tag="layer_list", width=-1, height=-1, border=False):
                                pass

                    # ── MIDDLE: canvas + global fields ────────────────────────
                    with dpg.table_cell():
                        with dpg.child_window(
                            tag="panel_mid",
                            width=-1, height=-1,
                            border=False, no_scrollbar=True,
                        ):
                            dpg.add_drawlist(tag="canvas_dl", width=400, height=10)
                            dpg.add_separator()
                            with dpg.child_window(
                                tag="fields_panel",
                                width=-1, height=215,
                                border=False,
                            ):
                                dpg.add_text(i18n.t("field_high_level"), tag="ui_text_high_label")
                                dpg.add_input_text(
                                    tag="inp_high", width=-1,
                                    multiline=True, height=52, default_value="",
                                )

                                with dpg.collapsing_header(
                                    label=i18n.t("field_style"),
                                    tag="ui_style_header",
                                    default_open=True,
                                ):
                                    dpg.add_text(i18n.t("field_style_aesthetics"), tag="ui_text_style_aesthetics")
                                    dpg.add_input_text(tag="inp_style_aesthetics", width=-1, default_value="")
                                    dpg.add_text(i18n.t("field_style_lighting"), tag="ui_text_style_lighting")
                                    dpg.add_input_text(tag="inp_style_lighting", width=-1, default_value="")
                                    dpg.add_text(i18n.t("field_style_art_style"), tag="ui_text_style_art_style")
                                    dpg.add_input_text(tag="inp_style_art_style", width=-1, default_value="")
                                    dpg.add_text(i18n.t("field_style_medium"), tag="ui_text_style_medium")
                                    dpg.add_input_text(tag="inp_style_medium", width=-1, default_value="")
                                    dpg.add_text(i18n.t("field_style_palette"), tag="ui_text_style_palette")
                                    dpg.add_input_text(tag="inp_style_palette", width=-1, default_value="")

                                dpg.add_text(i18n.t("field_background"), tag="ui_text_bg_label")
                                dpg.add_input_text(
                                    tag="inp_bg", width=-1,
                                    multiline=True, height=40, default_value="",
                                )

                    # ── RIGHT: properties ─────────────────────────────────────
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

        dpg.add_text(
            tag="status_bar",
            default_value=i18n.t("status_initial"),
        )
