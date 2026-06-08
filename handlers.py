"""handlers.py — mouse and keyboard event handlers."""
import dearpygui.dearpygui as dpg
import state
import config
import geometry
import draw
import panels
import history
import i18n


# ── Keyboard repeat guard ─────────────────────────────────────────────────────
# add_key_press_handler fires every frame while held — track first-press only
_z_was_held: bool = False


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


# ── Mouse state machine: press → drag → release ───────────────────────────────
#
# Единая модель без зависимости от app_data mouse_drag_handler'а.
# Все координаты — через geometry.mouse_to_rel() (canvas-относительные пиксели).
#
# Состояние:
#   st["pressed"]   — True пока кнопка зажата (детектирует фронт нажатия)
#   st["drag"]      — (mode, idx, orig_bbox, anchor_x, anchor_y, committed)
#   st["draw_start"]— точка старта рисования рамки в add_mode
#
# on_mouse_down фиксирует намерение (выбор / режим resize или move / рисование).
# on_mouse_move движет drag-состояние или обновляет превью рамки.
# on_mouse_release финализирует и сбрасывает состояние.

def _on_resize_handle(rx: float, ry: float, idx: int) -> bool:
    """True если точка (rx,ry) попадает в угловую ручку ресайза элемента idx."""
    x0, y0, x1, y1 = geometry.bbox_to_rel(state.st["elements"][idx]["bbox"])
    return x1 - config.HANDLE <= rx <= x1 and y1 - config.HANDLE <= ry <= y1


def on_mouse_down(sender, app_data):
    """Фронт нажатия: фиксируем намерение (выбор/move/resize/рисование)."""
    if state.st["pressed"]:
        return  # уже обрабатываем, ждём release
    state.st["pressed"] = True

    if not geometry.on_canvas():
        return

    rx, ry = geometry.mouse_to_rel()

    # ── Режим рисования нового элемента ──
    if state.st["add_mode"]:
        state.st["draw_start"] = (rx, ry)
        return

    # ── Проверяем ручку ресайза выделенного элемента ──
    i = state.st["selected"]
    if 0 <= i < len(state.st["elements"]):
        if _on_resize_handle(rx, ry, i):
            state.st["drag"] = ("resize", i, list(state.st["elements"][i]["bbox"]), rx, ry, False)
            return

    # ── Обычный hit-test по телу элемента ──
    hit = geometry.hit_test_at(rx, ry)
    if hit >= 0:
        panels.select(hit)
        state.st["drag"] = ("move", hit, list(state.st["elements"][hit]["bbox"]), rx, ry, False)
    else:
        panels.select(-1)


def on_mouse_move(sender, app_data):
    """Обновление превью рамки или применение drag-а."""
    # Превью при рисовании
    if state.st["add_mode"] and state.st["draw_start"]:
        draw.redraw()
        return

    if state.st["drag"] is None:
        return

    rx, ry = geometry.mouse_to_rel()
    mode, idx, orig, sx, sy, committed = state.st["drag"]
    cw, ch, _ = geometry.canvas_dims()
    dx = round((rx - sx) / cw * 1000)
    dy = round((ry - sy) / ch * 1000)

    if dx == 0 and dy == 0:
        return

    # Отложенный push_history: только при первом реальном сдвиге
    if not committed:
        history.push_history()
        state.st["drag"] = (mode, idx, orig, sx, sy, True)

    el = state.st["elements"][idx]
    if mode == "move":
        ymin, xmin, ymax, xmax = orig
        dx = max(-xmin, min(1000 - xmax, dx))
        dy = max(-ymin, min(1000 - ymax, dy))
        el["bbox"] = [ymin + dy, xmin + dx, ymax + dy, xmax + dx]
    else:  # resize
        def cl(v): return max(0, min(1000, v))
        el["bbox"] = [orig[0], orig[1], cl(orig[2] + dy), cl(orig[3] + dx)]

    for k, v in enumerate(el["bbox"]):
        tag = f"prop_bbox_{k}"
        if dpg.does_item_exist(tag):
            dpg.set_value(tag, v)
    draw.redraw()


def on_mouse_release(sender, app_data):
    """Финализация: создать элемент в draw_mode или завершить drag."""
    state.st["pressed"] = False

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
            panels.refresh_layers()
            panels.refresh_props()
        state.st["draw_start"] = None
        state.st["add_mode"] = None
        state.set_status(i18n.t("status_ready"))
        draw.redraw()
        return

    if state.st["drag"] is not None:
        state.st["drag"] = None
        panels.refresh_props()


# ── Keyboard handler ─────────────────────────────────────────────────────────
def on_key_press(sender, key):
    global _z_was_held
    if key == dpg.mvKey_Escape:
        if not _input_has_focus():
            state.st["add_mode"] = None
            state.st["draw_start"] = None
            state.set_status(i18n.t("status_ready"))
            draw.redraw()
    elif key == dpg.mvKey_Z:
        ctrl = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)
        if ctrl and not _input_has_focus() and not _z_was_held:
            history.undo()
        _z_was_held = True


def on_key_release(sender, key):
    global _z_was_held
    if key == dpg.mvKey_Z:
        _z_was_held = False


