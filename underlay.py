"""underlay.py — reference image underlay for the canvas.

Editor-only state: never written to the prompt JSON.

Public API:
  load(path)            — load image file, register DPG texture
  clear()               — hide underlay, queue texture for safe deletion
  flush_deletes()       — call from render loop to actually delete queued textures
  compute_uv(...)       — pure function: UV coords for stretch/crop fit
  draw_into_canvas()    — render underlay into canvas_dl (call from draw.redraw)

DPG 2.3.1 limitation: deleting a static_texture from within a callback causes
a segfault. Therefore clear() only hides the underlay and queues the tag;
flush_deletes() does the actual dpg.delete_item() from the safe render-loop context.
"""
import dearpygui.dearpygui as dpg
import state
import i18n

_TEX_TAG = "underlay_texture"
_IMG_TAG = "underlay_img"      # draw_image item inside canvas_dl
_TEX_REG = "tex_reg"           # persistent registry created in main.py

_delete_queue: list = []       # texture tags pending safe deletion


def load(path: str) -> None:
    """Load an image and register it as a DPG static texture."""
    # Queue any existing texture for deletion (safe — load is called from
    # file-dialog callback, but flush_deletes will run before next frame)
    _queue_delete_current()
    try:
        w, h, _, data = dpg.load_image(path)
    except Exception as e:
        state.set_status(i18n.t("underlay_error_load", err=e))
        return

    dpg.add_static_texture(width=w, height=h, default_value=data,
                           tag=_TEX_TAG, parent=_TEX_REG)

    ul = state.st["underlay"]
    ul["path"]        = path
    ul["texture_tag"] = _TEX_TAG
    ul["img_w"]       = w
    ul["img_h"]       = h
    ul["visible"]     = True
    state.set_status(i18n.t("underlay_loaded", name=_basename(path)))


def clear() -> None:
    """Hide the underlay and queue the texture for deletion.

    Does NOT call dpg.delete_item on the texture — that segfaults in DPG 2.3.1
    when called from a callback. The actual deletion happens in flush_deletes()
    which is called from the render loop.
    """
    # Remove the draw_image from canvas_dl immediately (this is safe)
    if dpg.does_item_exist(_IMG_TAG):
        dpg.delete_item(_IMG_TAG)
    # Queue the texture for deletion in the render loop
    _queue_delete_current()
    # Reset state so rendering stops using the texture right away
    ul = state.st["underlay"]
    ul["path"]        = None
    ul["texture_tag"] = None
    ul["img_w"]       = 0
    ul["img_h"]       = 0


def flush_deletes() -> None:
    """Delete queued textures. Call from the render loop (outside callbacks)."""
    while _delete_queue:
        tag = _delete_queue.pop()
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)


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

    canvas_ar = canvas_w / canvas_h
    image_ar  = img_w   / img_h

    if image_ar > canvas_ar:
        crop_w_uv = canvas_ar / image_ar
        u0 = (1.0 - crop_w_uv) / 2.0
        return (u0, 0.0), (u0 + crop_w_uv, 1.0)
    else:
        crop_h_uv = image_ar / canvas_ar
        v0 = (1.0 - crop_h_uv) / 2.0
        return (0.0, v0), (1.0, v0 + crop_h_uv)


def draw_into_canvas() -> None:
    """Render the underlay into canvas_dl after the background rectangle."""
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
        tag=_IMG_TAG,
        parent="canvas_dl",
    )


# ── Internal helpers ──────────────────────────────────────────────────────────

def _queue_delete_current() -> None:
    """Move the current texture tag into the delete queue (if one exists)."""
    tag = state.st["underlay"].get("texture_tag")
    if tag and tag not in _delete_queue:
        _delete_queue.append(tag)


def _basename(path: str) -> str:
    import os
    return os.path.basename(path)
