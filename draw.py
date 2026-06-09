"""draw.py — canvas redraw logic."""
import dearpygui.dearpygui as dpg
import state
import config
import geometry
import i18n
import underlay


def redraw() -> None:
    if not dpg.does_item_exist("canvas_dl"):
        return
    dpg.delete_item("canvas_dl", children_only=True)
    cw, ch, _ = geometry.canvas_dims()

    underlay.draw_into_canvas()

    dpg.draw_rectangle(
        [0, 0], [cw, ch],
        fill=(28, 28, 28, 255), color=(180, 180, 180, 255),
        thickness=2, parent="canvas_dl",
    )
    for p in [250, 500, 750]:
        gx = p / 1000 * cw
        gy = p / 1000 * ch
        dpg.draw_line([gx, 0], [gx, ch], color=(55, 55, 55, 180), thickness=1, parent="canvas_dl")
        dpg.draw_line([0, gy], [cw, gy], color=(55, 55, 55, 180), thickness=1, parent="canvas_dl")

    for i, el in enumerate(state.st["elements"]):
        x0, y0, x1, y1 = geometry.bbox_to_rel(el["bbox"])
        sel = (i == state.st["selected"])
        if el["type"] == "text":
            fill   = (60, 130, 230, 140) if not sel else (230, 190, 30, 160)
            border = (80, 160, 255, 255) if not sel else (255, 220, 40, 255)
        else:
            fill   = (50, 200, 100, 120) if not sel else (230, 190, 30, 140)
            border = (60, 210, 110, 255) if not sel else (255, 220, 40, 255)

        dpg.draw_rectangle(
            [x0, y0], [x1, y1],
            fill=fill, color=border,
            thickness=2 if sel else 1, parent="canvas_dl",
        )
        label = el.get("text") or el.get("desc", "")
        dpg.draw_text(
            [x0 + 3, y0 + 3],
            f"[{'T' if el['type'] == 'text' else 'O'}] {label[:28]}",
            color=(255, 255, 255, 210), size=11, parent="canvas_dl",
        )
        if sel:
            dpg.draw_rectangle(
                [x1 - config.HANDLE, y1 - config.HANDLE], [x1, y1],
                fill=(255, 220, 40, 255), color=(255, 255, 255, 200),
                thickness=1, parent="canvas_dl",
            )

    if state.st["draw_start"] and state.st["add_mode"]:
        rx, ry = geometry.mouse_to_rel()
        sx, sy = state.st["draw_start"]
        dpg.draw_rectangle(
            [sx, sy], [rx, ry],
            fill=(255, 200, 50, 60), color=(255, 200, 50, 220),
            thickness=1, parent="canvas_dl",
        )

    if state.st["add_mode"]:
        dpg.draw_text(
            [4, ch - 18],
            i18n.t("canvas_draw_hint", mode=state.st["add_mode"]),
            color=(255, 200, 50, 220), size=12, parent="canvas_dl",
        )
