#!/usr/bin/env python3
"""main.py — Ideogram4 Layout Editor entry point."""
import dearpygui.dearpygui as dpg

import config   # noqa: F401  (side-effect: makedirs PROMPTS_DIR)
import state
import handlers
import ui

# ── DPG init ──────────────────────────────────────────────────────────────────
dpg.create_context()

with dpg.font_registry():
    with dpg.font(config.FONT_PATH, 15) as default_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)

with dpg.handler_registry():
    dpg.add_mouse_click_handler(button=0,   callback=handlers.on_mouse_press)
    dpg.add_mouse_release_handler(button=0, callback=handlers.on_mouse_release)
    dpg.add_mouse_move_handler(             callback=handlers.on_mouse_move)
    dpg.add_key_press_handler(              callback=handlers.on_key_press)

ui.build_ui()

# ── Viewport setup ────────────────────────────────────────────────────────────
dpg.create_viewport(
    title="Ideogram4 Layout Editor",
    width=config.INIT_W, height=config.INIT_H,
    resizable=True, min_width=900, min_height=600,
)
dpg.setup_dearpygui()
dpg.bind_font(default_font)
dpg.show_viewport()
dpg.set_primary_window("main", True)
dpg.maximize_viewport()

handlers.on_preset(None, state.PRESET_NAMES[3])

# ── Render loop ───────────────────────────────────────────────────────────────
_prev_dl = (0, 0)
_prev_vp = (0, 0)

while dpg.is_dearpygui_running():
    vw = dpg.get_viewport_width()
    vh = dpg.get_viewport_height()

    # Sync main window and table height to viewport
    if (vw, vh) != _prev_vp:
        dpg.configure_item("main", width=vw, height=vh)
        panel_h = vh - 68   # toolbar + separator + statusbar
        dpg.configure_item("main_table", height=panel_h)
        _prev_vp = (vw, vh)

    # Sync canvas_dl size and cache its absolute position
    if dpg.does_item_exist("panel_mid"):
        # Canvas width from actual panel_mid rect; height from viewport arithmetic.
        # fields_panel is fixed at 215px; toolbar+sep+statusbar ≈ 68px; sep+pad ≈ 4px.
        mid_w = max(200, vw // 2 - 20)  # fallback until rect is ready
        try:
            pmin = dpg.get_item_rect_min("panel_mid")
            pmax = dpg.get_item_rect_max("panel_mid")
            mid_w = max(200, int(pmax[0] - pmin[0]) - 8)
        except Exception as _e:
            print("RENDER LOOP width ERR:", repr(_e))

        mid_h = max(200, vh - 68 - 215 - 14)  # table_h - fields - separators

        if (mid_w, mid_h) != _prev_dl:
            state.g_dl_w = mid_w
            state.g_dl_h = mid_h
            dpg.configure_item("canvas_dl", width=mid_w, height=mid_h)
            _prev_dl = (mid_w, mid_h)
            import draw
            draw.redraw()

        # Refresh cached canvas origin each frame (changes on viewport resize)
        try:
            dl_pos = dpg.get_item_rect_min("canvas_dl")
            state.g_dl_ox, state.g_dl_oy = dl_pos[0], dl_pos[1]
            state.g_canvas_ready = True
        except Exception as _e:
            print("RENDER LOOP origin ERR:", repr(_e))

    dpg.render_dearpygui_frame()

dpg.destroy_context()
