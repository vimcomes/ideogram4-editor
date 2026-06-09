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
    "underlay": {
        "path":        None,   # str | None — editor-only, never written to prompt JSON
        "texture_tag": None,
        "visible":     True,
        "opacity":     0.5,
        "fit":         "stretch",  # "stretch" | "crop"
        "img_w":       0,
        "img_h":       0,
    },
}

# ── Canvas geometry globals (updated each render frame) ───────────────────────
# IMPORTANT: other modules must access these as state.g_dl_w, NOT via
# "from state import g_dl_w" because the scalars are reassigned, not mutated.
g_dl_w: int = 400
g_dl_h: int = 540
g_dl_ox: int = 0     # absolute viewport X of canvas_dl top-left
g_dl_oy: int = 0     # absolute viewport Y of canvas_dl top-left
g_canvas_ready: bool = False  # True after first successful render-loop layout
g_style_mode: str = "art"    # "art" or "photo" — controls style_description key order
g_fields_h: int = 215        # fields_panel height, controlled by horizontal splitter
g_fields_h_init: bool = False  # True after first-frame init from real avail height
g_split_dragging: bool = False
g_split_prev_y:   float = 0.0
g_underlay_dirty: bool = False   # set by callbacks; render loop rebuilds underlay panel

# ── Resolution presets ────────────────────────────────────────────────────────
with open(config.PRESETS_FILE) as _f:
    PRESETS = json.load(_f)["presets"]
PRESET_NAMES = [p["name"] for p in PRESETS]


def set_status(msg: str) -> None:
    st["status"] = msg
    if dpg.does_item_exist("status_bar"):
        dpg.set_value("status_bar", msg)
