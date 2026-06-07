"""state.py — shared mutable state and presets."""
import json
import dearpygui.dearpygui as dpg
import config

# ── App state dict ────────────────────────────────────────────────────────────
st: dict = {
    "img_w": 1168,
    "img_h": 1712,
    "elements": [],
    "selected": -1,
    "add_mode": None,
    "drag": None,
    "draw_start": None,
    "pressed": False,
    "status": "",
}

# ── Canvas geometry globals (updated each render frame) ───────────────────────
# IMPORTANT: other modules must access these as state.g_dl_w, NOT via
# "from state import g_dl_w" because the scalars are reassigned, not mutated.
g_dl_w: int = 400
g_dl_h: int = 540
g_dl_ox: int = 0     # absolute viewport X of canvas_dl top-left
g_dl_oy: int = 0     # absolute viewport Y of canvas_dl top-left
g_canvas_ready: bool = False  # True after first successful render-loop layout
g_style_open: bool = True    # tracks collapsing_header state for canvas resize
g_fields_h: int = 215        # fields_panel height, updated when style header toggled

# ── Resolution presets ────────────────────────────────────────────────────────
with open(config.PRESETS_FILE) as _f:
    PRESETS = json.load(_f)["presets"]
PRESET_NAMES = [p["name"] for p in PRESETS]


def set_status(msg: str) -> None:
    st["status"] = msg
    if dpg.does_item_exist("status_bar"):
        dpg.set_value("status_bar", msg)
