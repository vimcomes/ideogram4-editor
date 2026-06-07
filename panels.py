"""panels.py — layer panel, properties panel, selection, and themes."""
import dearpygui.dearpygui as dpg
import state
import geometry
import draw
import history
import i18n

# ── Button themes ─────────────────────────────────────────────────────────────
_sel_btn_theme = None


def _ensure_themes() -> None:
    global _sel_btn_theme
    if _sel_btn_theme is not None:
        return
    with dpg.theme() as t:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button,        [160, 120, 10, 200])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [200, 160, 20, 230])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,  [230, 190, 40, 255])
    _sel_btn_theme = t


# ── Layer panel ───────────────────────────────────────────────────────────────
def refresh_layers() -> None:
    if not dpg.does_item_exist("layer_list"):
        return
    dpg.delete_item("layer_list", children_only=True)
    for i, el in enumerate(state.st["elements"]):
        label = el.get("text") or el.get("desc") or i18n.t("layer_empty_label")
        typ   = "T" if el["type"] == "text" else "O"
        col_t = (80, 160, 255, 255) if typ == "T" else (60, 210, 110, 255)
        sel   = (i == state.st["selected"])

        with dpg.group(horizontal=True, parent="layer_list"):
            dpg.add_text(f"[{typ}]", color=col_t)

            def make_sel(idx):
                def cb(s, u): select(idx)
                return cb

            btn = dpg.add_button(
                label=f"{label[:18]}",
                tag=f"layer_btn_{i}",
                width=-1,
                callback=make_sel(i),
            )
            if sel:
                _ensure_themes()
                dpg.bind_item_theme(btn, _sel_btn_theme)


# ── Properties panel ──────────────────────────────────────────────────────────
def refresh_props() -> None:
    if not dpg.does_item_exist("props_group"):
        return
    dpg.delete_item("props_group", children_only=True)
    i = state.st["selected"]
    if i < 0 or i >= len(state.st["elements"]):
        dpg.add_text(i18n.t("props_no_selection"), parent="props_group", color=(160, 160, 160, 255))
        return

    el = state.st["elements"][i]
    dpg.add_text(i18n.t("props_layer_title", index=i), parent="props_group", color=(220, 220, 100, 255))
    dpg.add_separator(parent="props_group")

    def set_type(_, val):
        history.push_history()
        el["type"] = val
        if el["type"] == "text" and "text" not in el:
            el["text"] = ""
        refresh_props()
        refresh_layers()
        draw.redraw()

    dpg.add_text(i18n.t("props_type_label"), parent="props_group")
    dpg.add_radio_button(
        ["text", "obj"],
        default_value=el["type"],
        horizontal=True,
        callback=set_type,
        parent="props_group",
    )
    dpg.add_separator(parent="props_group")

    if el["type"] == "text":
        dpg.add_text(i18n.t("props_text_label"), parent="props_group")

        def cb_text(s, v):
            el["text"] = v
            btn_tag = f"layer_btn_{state.st['selected']}"
            if dpg.does_item_exist(btn_tag):
                dpg.set_item_label(btn_tag, (v or i18n.t("layer_empty_label"))[:18])
            draw.redraw()

        dpg.add_input_text(
            default_value=el.get("text", ""),
            width=-1,
            callback=cb_text,
            tag="prop_text",
            parent="props_group",
        )

    dpg.add_text(i18n.t("props_desc_label"), parent="props_group")

    def cb_desc(s, v):
        el["desc"] = v
        if el.get("type") != "text":
            btn_tag = f"layer_btn_{state.st['selected']}"
            if dpg.does_item_exist(btn_tag):
                dpg.set_item_label(btn_tag, (v or i18n.t("layer_empty_label"))[:18])
        draw.redraw()

    dpg.add_input_text(
        default_value=el.get("desc", ""),
        width=-1,
        multiline=True,
        height=100,
        callback=cb_desc,
        tag="prop_desc",
        parent="props_group",
    )

    dpg.add_separator(parent="props_group")
    dpg.add_text(i18n.t("props_bbox_label"), parent="props_group")
    bbox = el["bbox"]

    def make_bbox_cb(idx):
        def cb(s, v):
            el["bbox"][idx] = int(v)
            draw.redraw()
        return cb

    with dpg.group(horizontal=True, parent="props_group"):
        for idx, lbl in enumerate(["ymin", "xmin", "ymax", "xmax"]):
            with dpg.group():
                dpg.add_text(lbl)
                dpg.add_input_int(
                    default_value=bbox[idx],
                    width=82,
                    min_value=0,
                    max_value=1000,
                    callback=make_bbox_cb(idx),
                    tag=f"prop_bbox_{idx}",
                )

    dpg.add_separator(parent="props_group")
    dpg.add_text(i18n.t("props_palette_label"), parent="props_group")
    pal_str = ", ".join(el.get("color_palette", []))

    def cb_pal(s, v):
        el["color_palette"] = [c.strip() for c in v.split(",") if c.strip()]

    dpg.add_input_text(
        default_value=pal_str,
        width=-1,
        callback=cb_pal,
        parent="props_group",
    )


# ── Selection ─────────────────────────────────────────────────────────────────
def select(idx: int) -> None:
    state.st["selected"] = idx
    refresh_layers()
    refresh_props()
    draw.redraw()


# ── Convenience ───────────────────────────────────────────────────────────────
def refresh_all() -> None:
    refresh_layers()
    refresh_props()
    draw.redraw()
