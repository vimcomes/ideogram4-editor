"""handlers.py — mouse, keyboard, and toolbar event handlers."""
import dearpygui.dearpygui as dpg
import state
import config
import geometry
import draw
import panels
import history
import prompt_io


# ── Focus helpers ─────────────────────────────────────────────────────────────
def _input_has_focus() -> bool:
    focused = dpg.get_focused_item()
    if not focused:
        return False
    try:
        itype = dpg.get_item_type(focused)
        return "InputText" in itype or "InputInt" in itype
    except Exception:
        return False


# ── Mouse handlers ────────────────────────────────────────────────────────────
def on_mouse_press(sender, app_data):
    if not geometry.on_canvas():
        return
    rx, ry = geometry.mouse_to_rel()

    if state.st["add_mode"]:
        state.st["draw_start"] = (rx, ry)
        return

    i = state.st["selected"]
    if 0 <= i < len(state.st["elements"]):
        x0, y0, x1, y1 = geometry.bbox_to_rel(state.st["elements"][i]["bbox"])
        if x1 - config.HANDLE <= rx <= x1 and y1 - config.HANDLE <= ry <= y1:
            # committed=False: push_history deferred until first real drag movement
            state.st["drag"] = ("resize", i, list(state.st["elements"][i]["bbox"]), rx, ry, False)
            return

    hit = geometry.hit_test()
    if hit >= 0:
        # committed=False: push_history deferred until first real drag movement
        state.st["drag"] = ("move", hit, list(state.st["elements"][hit]["bbox"]), rx, ry, False)
        panels.select(hit)
    else:
        panels.select(-1)


def on_mouse_release(sender, app_data):
    if state.st["add_mode"] and state.st["draw_start"]:
        rx, ry = geometry.mouse_to_rel()
        sx, sy = state.st["draw_start"]
        if abs(rx - sx) * abs(ry - sy) > config.MIN_AREA_PX:
            history.push_history()
            bbox = geometry.rel_to_bbox(sx, sy, rx, ry)
            el = {"type": state.st["add_mode"], "bbox": bbox, "desc": "", "color_palette": []}
            if state.st["add_mode"] == "text":
                el["text"] = ""
            state.st["elements"].append(el)
            state.st["selected"] = len(state.st["elements"]) - 1
            # refresh layers and props first, then clear state and redraw
            panels.refresh_layers()
            panels.refresh_props()
        state.st["draw_start"] = None
        state.st["add_mode"] = None
        state.set_status("Готов.")
        draw.redraw()
        return
    state.st["drag"] = None


def on_mouse_move(sender, app_data):
    if state.st["add_mode"] and state.st["draw_start"]:
        draw.redraw()
        return
    if not state.st["drag"]:
        return

    rx, ry = geometry.mouse_to_rel()
    mode, idx, orig, sx, sy, committed = state.st["drag"]
    cw, ch, _ = geometry.canvas_dims()
    dx = round((rx - sx) / cw * 1000)
    dy = round((ry - sy) / ch * 1000)

    if dx == 0 and dy == 0:
        return

    # Push history on first actual movement
    if not committed:
        history.push_history()
        state.st["drag"] = (mode, idx, orig, sx, sy, True)

    el = state.st["elements"][idx]
    if mode == "move":
        ymin, xmin, ymax, xmax = orig
        dx = max(-xmin, min(1000 - xmax, dx))
        dy = max(-ymin, min(1000 - ymax, dy))
        el["bbox"] = [ymin + dy, xmin + dx, ymax + dy, xmax + dx]
    else:
        def cl(v): return max(0, min(1000, v))
        el["bbox"] = [orig[0], orig[1], cl(orig[2] + dy), cl(orig[3] + dx)]

    for k, v in enumerate(el["bbox"]):
        tag = f"prop_bbox_{k}"
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, v)
    draw.redraw()


def on_key_press(sender, key):
    if key == dpg.mvKey_Escape:
        if not _input_has_focus():
            state.st["add_mode"] = None
            state.st["draw_start"] = None
            state.set_status("Готов.")
            draw.redraw()
    elif key == dpg.mvKey_Z:
        ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
        if ctrl and not _input_has_focus():
            history.undo()


# ── Toolbar callbacks ─────────────────────────────────────────────────────────
def add_text(s, u):
    state.st["add_mode"] = "text"
    state.set_status("Нарисуй bbox для [text]  (Esc = отмена)")


def add_obj(s, u):
    state.st["add_mode"] = "obj"
    state.set_status("Нарисуй bbox для [obj]  (Esc = отмена)")


def del_selected(s, u):
    i = state.st["selected"]
    if i < 0 or i >= len(state.st["elements"]):
        return
    history.push_history()
    state.st["elements"].pop(i)
    state.st["selected"] = min(i, len(state.st["elements"]) - 1)
    panels.refresh_all()


def move_up(s, u):
    i = state.st["selected"]
    if i <= 0 or i >= len(state.st["elements"]):
        return
    history.push_history()
    state.st["elements"][i], state.st["elements"][i - 1] = (
        state.st["elements"][i - 1], state.st["elements"][i]
    )
    state.st["selected"] = i - 1
    panels.refresh_all()


def move_down(s, u):
    i = state.st["selected"]
    if i < 0 or i >= len(state.st["elements"]) - 1:
        return
    history.push_history()
    state.st["elements"][i], state.st["elements"][i + 1] = (
        state.st["elements"][i + 1], state.st["elements"][i]
    )
    state.st["selected"] = i + 1
    panels.refresh_all()


def on_preset(s, name):
    for p in state.PRESETS:
        if p["name"] == name:
            state.st["img_w"], state.st["img_h"] = p["w"], p["h"]
            break
    draw.redraw()
