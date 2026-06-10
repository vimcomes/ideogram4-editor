#!/usr/bin/env python3
"""main.py — Ideogram4 Layout Editor entry point."""
import dearpygui.dearpygui as dpg

import config   # noqa: F401  (side-effect: makedirs PROMPTS_DIR)
import state
import handlers
import toolbar
import theme
import ui
from version import __version__

# ── DPG init ──────────────────────────────────────────────────────────────────
dpg.create_context()
theme.apply_theme()

# Single persistent texture registry for all dynamic textures (underlay, etc.)
dpg.add_texture_registry(tag="tex_reg")

with dpg.font_registry():
    with dpg.font(config.FONT_PATH, 15) as default_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)

with dpg.handler_registry():
    dpg.add_mouse_down_handler(button=0,     callback=handlers.on_mouse_down)
    dpg.add_mouse_move_handler(              callback=handlers.on_mouse_move)
    dpg.add_mouse_release_handler(button=0,  callback=handlers.on_mouse_release)
    dpg.add_key_press_handler(               callback=handlers.on_key_press)
    dpg.add_key_release_handler(             callback=handlers.on_key_release)

ui.build_ui()

# ── Splitter themes (created after build_ui so context is ready) ──────────────
with dpg.theme() as _sp_normal:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (69, 71, 90, 80))
with dpg.theme() as _sp_hot:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (137, 180, 250, 180))
dpg.bind_item_theme("splitter_h", _sp_normal)

# ── Viewport setup ────────────────────────────────────────────────────────────
dpg.create_viewport(
    title=f"Ideogram4 Layout Editor  v{__version__}",
    width=config.INIT_W, height=config.INIT_H,
    resizable=True, min_width=900, min_height=600,
)
dpg.setup_dearpygui()
dpg.bind_font(default_font)
dpg.show_viewport()
dpg.set_primary_window("main", True)
dpg.maximize_viewport()

toolbar.on_preset(None, state.PRESET_NAMES[3])
import panels as _panels
_panels.refresh_underlay_panel()

# ── Render loop ───────────────────────────────────────────────────────────────
_prev_dl       = (0, 0)
_prev_vp       = (0, 0)
_prev_fields_h = 215

while dpg.is_dearpygui_running():
    vw = dpg.get_viewport_width()
    vh = dpg.get_viewport_height()

    if (vw, vh) != _prev_vp:
        dpg.configure_item("main", width=vw, height=vh)
        _prev_vp = (vw, vh)

    if dpg.does_item_exist("panel_mid"):

        # ── Horizontal splitter drag ──────────────────────────────────────────
        try:
            sp_hov = dpg.get_item_state("splitter_h").get("hovered", False)
            if sp_hov or state.g_split_dragging:
                dpg.bind_item_theme("splitter_h", _sp_hot)
            else:
                dpg.bind_item_theme("splitter_h", _sp_normal)

            if sp_hov and dpg.is_mouse_button_down(0) and not state.g_split_dragging:
                state.g_split_dragging = True
                state.g_split_prev_y = dpg.get_mouse_pos(local=False)[1]

            if state.g_split_dragging:
                if dpg.is_mouse_button_down(0):
                    my = dpg.get_mouse_pos(local=False)[1]
                    dy = my - state.g_split_prev_y
                    state.g_split_prev_y = my
                    # drag down → splitter moves down → canvas taller → fields shorter
                    state.g_fields_h = max(60, state.g_fields_h - int(dy))
                else:
                    state.g_split_dragging = False
        except Exception:
            pass

        try:
            avail    = dpg.get_item_state("panel_mid")["content_region_avail"]
            avail_h  = int(avail[1])
            mid_w    = max(200, int(avail[0]) - 4)
        except Exception:
            avail_h  = vh - 80
            mid_w    = max(200, vw // 2 - 20)

        # first frame: init split position to 1/3 of available height
        if not state.g_fields_h_init and avail_h > 200:
            state.g_fields_h      = avail_h // 3
            state.g_fields_h_init = True

        # clamp so canvas always has at least 100px
        state.g_fields_h = max(60, min(state.g_fields_h, avail_h - 100))

        fields_h = state.g_fields_h
        # 6px splitter + item spacings
        mid_h = max(100, avail_h - fields_h - 18)

        if fields_h != _prev_fields_h:
            dpg.configure_item("fields_panel", height=fields_h)
            _prev_fields_h = fields_h

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

    import native_dialog as _nd
    _nd.flush()

    import underlay as _ul
    _ul.flush_deletes()

    if state.g_underlay_dirty:
        state.g_underlay_dirty = False
        import panels
        panels.refresh_underlay_panel()

    dpg.render_dearpygui_frame()

dpg.destroy_context()
