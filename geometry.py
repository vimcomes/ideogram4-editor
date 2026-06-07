"""geometry.py — coordinate transforms between canvas and image space."""
import dearpygui.dearpygui as dpg
import state
import config


def canvas_dims() -> tuple[int, int, float]:
    """Returns (draw_w, draw_h, scale) based on actual drawlist size."""
    iw, ih = state.st["img_w"], state.st["img_h"]
    avail_w = max(100, state.g_dl_w - 4)
    avail_h = max(100, state.g_dl_h - 4)
    scale = min(avail_w / iw, avail_h / ih)
    return int(iw * scale), int(ih * scale), scale


def bbox_to_rel(bbox: list) -> tuple[float, float, float, float]:
    """[ymin,xmin,ymax,xmax] 0-1000 → drawlist-relative px (x0,y0,x1,y1)."""
    ymin, xmin, ymax, xmax = bbox
    cw, ch, _ = canvas_dims()
    return xmin / 1000 * cw, ymin / 1000 * ch, xmax / 1000 * cw, ymax / 1000 * ch


def rel_to_bbox(rx0: float, ry0: float, rx1: float, ry1: float) -> list:
    """Drawlist-relative px → [ymin,xmin,ymax,xmax] 0-1000."""
    cw, ch, _ = canvas_dims()

    def cl(v):
        return max(0, min(1000, round(v)))

    return [
        cl(min(ry0, ry1) / ch * 1000), cl(min(rx0, rx1) / cw * 1000),
        cl(max(ry0, ry1) / ch * 1000), cl(max(rx0, rx1) / cw * 1000),
    ]


def mouse_to_rel() -> tuple[float, float]:
    """Mouse position relative to canvas_dl top-left corner."""
    mx, my = dpg.get_mouse_pos(local=False)
    return mx - state.g_dl_ox, my - state.g_dl_oy


def on_canvas() -> bool:
    """Returns True if the mouse is inside the canvas area."""
    if not state.g_canvas_ready:
        return False
    rx, ry = mouse_to_rel()
    cw, ch, _ = canvas_dims()
    return 0 <= rx <= cw and 0 <= ry <= ch


def hit_test() -> int:
    """Returns the index of the topmost element under the mouse, or -1."""
    rx, ry = mouse_to_rel()
    return hit_test_at(rx, ry)


def hit_test_at(rx: float, ry: float) -> int:
    """Returns the index of the topmost element at given canvas-relative coords."""
    best = -1
    for i, el in enumerate(state.st["elements"]):
        x0, y0, x1, y1 = bbox_to_rel(el["bbox"])
        if x0 <= rx <= x1 and y0 <= ry <= y1:
            best = i
    return best
