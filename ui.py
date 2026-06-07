"""ui.py — builds the DPG window, dialogs, and three-column table layout."""
import dearpygui.dearpygui as dpg
import state
import config
import handlers
import prompt_io


def _open_file(s, u):
    if dpg.does_item_exist("open_dlg"):
        dpg.show_item("open_dlg")


def _save_file(s, u):
    if dpg.does_item_exist("save_dlg"):
        dpg.show_item("save_dlg")


def build_ui() -> None:
    # ── File dialogs ──────────────────────────────────────────────────────────
    with dpg.file_dialog(
        tag="open_dlg",
        label="Открыть промпт",
        callback=prompt_io.on_open_selected,
        cancel_callback=lambda s, a: None,
        default_path=config.PROMPTS_DIR,
        width=700, height=440,
        show=False, modal=True,
    ):
        dpg.add_file_extension(".*",    color=(200, 200, 200, 255), custom_text="Все файлы")
        dpg.add_file_extension(".json", color=(100, 220, 100, 255), custom_text="JSON промпт")
        dpg.add_file_extension(".txt",  color=(220, 200, 80, 255),  custom_text="TXT + JSON")

    with dpg.file_dialog(
        tag="save_dlg",
        label="Сохранить промпт",
        callback=prompt_io.on_save_selected,
        cancel_callback=lambda s, a: None,
        default_path=config.PROMPTS_DIR,
        default_filename="prompt.json",
        width=700, height=440,
        show=False, modal=True,
    ):
        dpg.add_file_extension(".*",    color=(200, 200, 200, 255), custom_text="Все файлы")
        dpg.add_file_extension(".json", color=(100, 220, 100, 255), custom_text="JSON промпт")

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
            dpg.add_text("Разрешение:")
            dpg.add_combo(
                state.PRESET_NAMES,
                default_value=state.PRESET_NAMES[3],
                width=185,
                callback=handlers.on_preset,
            )
            dpg.add_button(label="📋 Копировать JSON", callback=prompt_io.copy_to_clipboard)
            dpg.add_button(label="📂 Открыть",         callback=_open_file)
            dpg.add_button(label="💾 Сохранить",        callback=_save_file)
            dpg.add_button(label="↩ Undo (Ctrl+Z)",    callback=lambda s, u: __import__("history").undo())

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
                        dpg.add_text("Слои", color=(200, 200, 100, 255))
                        dpg.add_separator()
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="+ T", width=55, callback=handlers.add_text)
                            dpg.add_button(label="+ O", width=55, callback=handlers.add_obj)
                        dpg.add_separator()

                        with dpg.child_window(tag="layer_list", width=-1, height=-1, border=False):
                            pass

                        dpg.add_separator()
                        dpg.add_button(label="↑ Выше",    width=-1, callback=handlers.move_up)
                        dpg.add_button(label="↓ Ниже",    width=-1, callback=handlers.move_down)
                        dpg.add_button(label="✕ Удалить", width=-1, callback=handlers.del_selected)

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
                            dpg.add_text("High-level description:")
                            dpg.add_input_text(
                                tag="inp_high", width=-1,
                                multiline=True, height=48, default_value="",
                            )
                            dpg.add_text("Style description (JSON):")
                            dpg.add_input_text(
                                tag="inp_style", width=-1,
                                multiline=True, height=42, default_value="",
                            )
                            dpg.add_text("Background:")
                            dpg.add_input_text(tag="inp_bg", width=-1, default_value="")

                # ── RIGHT: properties ─────────────────────────────────────────
                with dpg.table_cell():
                    with dpg.child_window(tag="panel_right", width=-1, height=-1, border=True):
                        dpg.add_text("Свойства слоя", color=(200, 200, 100, 255))
                        dpg.add_separator()
                        with dpg.child_window(
                            tag="props_group",
                            width=-1, height=-1,
                            border=False,
                        ):
                            dpg.add_text("← Выбери слой", color=(160, 160, 160, 255))

        dpg.add_separator()
        dpg.add_text(
            tag="status_bar",
            default_value="Ctrl+Z = undo  |  Esc = отмена режима рисования",
        )
