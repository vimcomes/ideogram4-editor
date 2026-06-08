# Ideogram4 Layout Editor — Claude Instructions

## Project overview
GUI layer editor for Ideogram 4 image generation prompts (like Photoshop layer panel).
User places bbox regions on a canvas, sets properties, exports a JSON prompt.

## Stack
- Python + DearPyGui 2.3.1 (immediate-mode GPU GUI, no web/HTML)
- No ML dependencies

## Run & test
```bash
./run.sh                          # launch app
venv/bin/python -m pytest -q      # run all tests (must stay green)
```

## Architecture
| File | Responsibility |
|------|---------------|
| `state.py` | Global mutable state (`st` dict) + canvas geometry globals |
| `geometry.py` | Coordinate transforms: bbox↔canvas pixels, hit-test, mouse→canvas |
| `handlers.py` | Mouse FSM (press→drag→release) + keyboard |
| `toolbar.py` | Toolbar callbacks: add_text, add_obj, new_document, on_preset, on_lang_change |
| `ui.py` | DPG window layout (3-column table: layers | canvas+fields | properties) |
| `panels.py` | Layer list + properties panel (dynamic rebuild) |
| `draw.py` | Drawlist rendering of elements |
| `prompt_io.py` | Save/load JSON, clipboard, overwrite confirmation |
| `history.py` | Undo/redo |
| `i18n.py` | RU/EN strings, default lang = EN |
| `main.py` | Entry point + render loop (syncs canvas size every frame) |

## Key conventions
- **bbox format**: `[ymin, xmin, ymax, xmax]` in 0–1000 range (relative, resolution-independent)
- **Mouse coords**: always `get_mouse_pos(local=False)` (viewport-space, matches `rect_min`)
- **Canvas size**: `state.g_dl_w/h` set by render loop; `geometry.canvas_dims()` computes drawable area
- **Icons**: DejaVu-safe Unicode only — no emoji (break on Windows). Confirmed via fonttools.
- **Font**: bundled `assets/fonts/DejaVuSans.ttf`, resolved by `config._find_font()`

## Git workflow
- All changes → `develop` branch
- PR → merge into `master` only after user approval
- Commit after each logical unit of work

## DPG gotchas (DPG 2.3.1)
- `add_collapsing_header` does NOT support `callback=` kwarg → use render-loop polling instead
- `modal=True` windows cannot be shown via `configure_item(show=True)` from a callback → use `show_item()` / `hide_item()`
- Dynamic `dpg.window()` created inside a callback is invisible when `set_primary_window` is active → pre-build in `build_ui()` with `show=False`
- `get_mouse_pos()` default `local=True` returns window-relative coords; use `local=False` for viewport-space
- `add_font_range_hint` is a no-op in 2.3.1 (ranges are automatic) — suppress the DeprecationWarning or remove
- `pos=` in `configure_item` is ignored for windows; use `set_item_pos()` separately before `show_item()`

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
