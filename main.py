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
    dpg.add_mouse_down_handler(button=0,     callback=handlers.on_mouse_down)
    dpg.add_mouse_move_handler(              callback=handlers.on_mouse_move)
    dpg.add_mouse_release_handler(button=0,  callback=handlers.on_mouse_release)
    dpg.add_key_press_handler(               callback=handlers.on_key_press)

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

    if (vw, vh) != _prev_vp:
        dpg.configure_item("main", width=vw, height=vh)
        dpg.configure_item("main_table", height=vh - 68)
        _prev_vp = (vw, vh)

    if dpg.does_item_exist("panel_mid"):
        try:
            avail = dpg.get_item_state("panel_mid")["content_region_avail"]
            mid_w = max(200, int(avail[0]) - 4)
            mid_h = max(200, int(avail[1]) - 215 - 14)
        except Exception:
            mid_w = max(200, vw // 2 - 20)
            mid_h = max(200, vh - 68 - 215 - 14)

        if (mid_w, mid_h) != _prev_dl:
            state.g_dl_w = mid_w
            state.g_dl_h = mid_h
            dpg.configure_item("canvas_dl", width=mid_w, height=mid_h)
            _prev_dl = (mid_w, mid_h)
            import draw
            draw.redraw()

        try:
            rm = dpg.get_item_state("canvas_dl")["rect_min"]
            state.g_dl_ox = int(rm[0])
            state.g_dl_oy = int(rm[1])
            state.g_canvas_ready = True
        except Exception:
            pass

    dpg.render_dearpygui_frame()

dpg.destroy_context()
