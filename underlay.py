"""underlay.py — reference image underlay for the canvas.

Editor-only state: never written to the prompt JSON.

Public API:
  load(path)            — load image file, register DPG texture
  clear()               — remove texture, reset state
  compute_uv(...)       — pure function: UV coords for stretch/crop fit
  draw_into_canvas()    — render underlay into canvas_dl (call from draw.redraw)
"""
import dearpygui.dearpygui as dpg
import state
import i18n


def load(path: str) -> None:
    """Load an image and register it as a DPG static texture."""
    _clear_texture()
    try:
        w, h, _, data = dpg.load_image(path)
    except Exception as e:
        state.set_status(i18n.t("underlay_error_load", err=e))
        return

    with dpg.texture_registry():
        tag = dpg.add_static_texture(width=w, height=h, default_value=data,
                                     tag="underlay_texture")

    ul = state.st["underlay"]
    ul["path"]        = path
    ul["texture_tag"] = tag
    ul["img_w"]       = w
    ul["img_h"]       = h
    ul["visible"]     = True
    state.set_status(i18n.t("underlay_loaded", name=_basename(path)))


def clear() -> None:
    """Remove the underlay texture and reset state."""
    _clear_texture()
    ul = state.st["underlay"]
    ul["path"]        = None
    ul["texture_tag"] = None
    ul["img_w"]       = 0
    ul["img_h"]       = 0


def compute_uv(
    img_w: int, img_h: int,
    canvas_w: int, canvas_h: int,
    fit: str,
) -> tuple:
    """Return (uv_min, uv_max) for the given fit mode.

    fit='stretch' → full image fills canvas (may distort).
    fit='crop'    → centre-crop to canvas aspect, no distortion.
    """
    if fit == "stretch" or img_w == 0 or img_h == 0:
        return (0.0, 0.0), (1.0, 1.0)

    # crop: find the largest rect in image space that matches canvas aspect
    canvas_ar = canvas_w / canvas_h
    image_ar  = img_w   / img_h

    if image_ar > canvas_ar:
        # image is wider than canvas → crop left/right
        crop_w_uv = canvas_ar / image_ar
        u0 = (1.0 - crop_w_uv) / 2.0
        return (u0, 0.0), (u0 + crop_w_uv, 1.0)
    else:
        # image is taller than canvas → crop top/bottom
        crop_h_uv = image_ar / canvas_ar
        v0 = (1.0 - crop_h_uv) / 2.0
        return (0.0, v0), (1.0, v0 + crop_h_uv)


def draw_into_canvas() -> None:
    """Render the underlay into canvas_dl. Call at the start of draw.redraw()."""
    ul = state.st["underlay"]
    if not ul["texture_tag"] or not ul["visible"]:
        return
    if not dpg.does_item_exist(ul["texture_tag"]):
        return

    import geometry
    cw, ch, _ = geometry.canvas_dims()
    uv_min, uv_max = compute_uv(ul["img_w"], ul["img_h"], cw, ch, ul["fit"])
    alpha = max(0, min(255, int(ul["opacity"] * 255)))

    dpg.draw_image(
        ul["texture_tag"],
        pmin=[0, 0],
        pmax=[cw, ch],
        uv_min=uv_min,
        uv_max=uv_max,
        color=(255, 255, 255, alpha),
        parent="canvas_dl",
    )


# ── Internal helpers ──────────────────────────────────────────────────────────

def _clear_texture() -> None:
    tag = state.st["underlay"].get("texture_tag")
    if tag and dpg.does_item_exist(tag):
        dpg.delete_item(tag)


def _basename(path: str) -> str:
    import os
    return os.path.basename(path)
