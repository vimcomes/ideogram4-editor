"""colorwidget.py — reusable color-picker button for hex palette fields.

Provides:
  rgb_to_hex(rgb)              — pure function, GUI-free, testable
  append_hex(existing, hex)    — pure function, GUI-free, testable
  build_ui()                   — called once from ui.build_ui() to pre-build the modal
  build_palette_button(parent, target_input_tag, on_change=None)
                               — places a ◐ button that opens the shared modal picker
"""
import dearpygui.dearpygui as dpg
import i18n

# ── Module-level state for the shared modal ───────────────────────────────────
_target_tag: str = ""          # input widget whose value we update on OK
_on_change_cb = None           # optional callback(new_value) — needed for element palette
                                # where set_value does NOT trigger the widget's own callback


# ── Pure helper functions (GUI-free, fully testable) ──────────────────────────

def rgb_to_hex(rgb) -> str:
    """Convert DPG color (list/tuple of 3-4 floats 0-255) to '#rrggbb' string."""
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    return f"#{r:02x}{g:02x}{b:02x}"


def append_hex(existing: str, hex_val: str) -> str:
    """Append hex_val to an existing comma-separated palette string.

    Handles:
      ""          → "#aabbcc"
      "#aabbcc"   → "#aabbcc, #112233"
      "#aabbcc, " → "#aabbcc, #112233"  (trailing comma/space ignored)
    """
    cleaned = existing.strip().rstrip(",").strip()
    if cleaned:
        return f"{cleaned}, {hex_val}"
    return hex_val


# ── Shared modal (pre-built once in build_ui()) ───────────────────────────────

def build_ui() -> None:
    """Pre-build the color-picker modal window.  Call once from ui.build_ui()."""
    with dpg.window(
        tag="colorpicker_dlg",
        label=i18n.t("colorpicker_title"),
        show=False,
        modal=True,
        no_close=True,
        width=420,
        height=440,
        no_move=True,
        no_resize=True,
        no_collapse=True,
    ):
        dpg.add_color_picker(
            tag="colorpicker_widget",
            default_value=(255, 0, 0, 255),
            no_alpha=True,
            display_rgb=True,
            display_hex=True,
            picker_mode=dpg.mvColorPicker_wheel,
            width=300,
        )
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(
                tag="colorpicker_ok",
                label=i18n.t("colorpicker_ok"),
                width=120,
                callback=_on_ok,
            )
            dpg.add_button(
                label=i18n.t("colorpicker_cancel"),
                width=120,
                callback=_on_cancel,
            )


# ── Button factory ────────────────────────────────────────────────────────────

def build_palette_button(parent, target_input_tag: str, on_change=None) -> None:
    """Add a ◐ button next to *parent* that opens the shared color picker.

    Args:
        parent:            DPG parent item to place the button in.
        target_input_tag:  Tag of the input_text widget to append hex into.
        on_change:         Optional callable(new_value: str) invoked after
                           set_value — needed when the widget callback won't
                           fire (DPG does not call callbacks on set_value).
    """
    def _open(s, u):
        global _target_tag, _on_change_cb
        _target_tag    = target_input_tag
        _on_change_cb  = on_change
        _center_and_show()

    btn = dpg.add_button(label="◐", width=24, callback=_open, parent=parent)
    with dpg.tooltip(btn):
        dpg.add_text(i18n.t("colorpicker_tooltip"))


# ── Internal callbacks ────────────────────────────────────────────────────────

def _center_and_show() -> None:
    vw = dpg.get_viewport_width()
    vh = dpg.get_viewport_height()
    dpg.set_item_pos("colorpicker_dlg", [vw // 2 - 210, vh // 2 - 220])
    dpg.show_item("colorpicker_dlg")


def _on_ok(s, u) -> None:
    global _target_tag, _on_change_cb
    dpg.hide_item("colorpicker_dlg")
    if not _target_tag or not dpg.does_item_exist(_target_tag):
        return
    raw   = dpg.get_value("colorpicker_widget")   # list [r,g,b,a] 0-255
    hex_  = rgb_to_hex(raw)
    old   = dpg.get_value(_target_tag)
    new   = append_hex(old, hex_)
    dpg.set_value(_target_tag, new)
    if _on_change_cb is not None:
        _on_change_cb(new)
    _target_tag   = ""
    _on_change_cb = None


def _on_cancel(s, u) -> None:
    dpg.hide_item("colorpicker_dlg")
    global _target_tag, _on_change_cb
    _target_tag   = ""
    _on_change_cb = None
