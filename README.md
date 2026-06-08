# Ideogram4 Layout Editor

> GUI layer editor for composing structured [Ideogram 4](https://ideogram.ai/) image-generation prompts

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![DearPyGui 2.3.1](https://img.shields.io/badge/DearPyGui-2.3.1-orange)

![Ideogram4 Layout Editor](assets/screenshot.png)

## What it is

Ideogram 4 supports structured JSON prompts where each region of the image is described separately with a bounding box. Writing these prompts by hand is tedious. This editor lets you draw bbox regions on a canvas (like Photoshop's layer panel), set text/style properties per layer, and export a ready-to-paste JSON prompt in one click.

## Features

- Draw and resize `text` / `obj` bbox layers on a proportional canvas
- Layer panel with drag-to-reorder, show/hide, delete
- Properties panel: description, color palette, optional text content
- Undo / redo (`Ctrl+Z` / `Ctrl+Y`)
- Save / load JSON, copy prompt to clipboard
- 8 resolution presets (9:16 portrait → 16:9 landscape)
- RU / EN UI language switch
- Dark theme (Catppuccin Mocha)
- Draggable horizontal splitter between canvas and style fields

## Install

```bash
git clone https://github.com/vimcomes/ideogram4-editor.git
cd ideogram4-editor
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
./run.sh          # Linux / macOS  (creates venv automatically on first run)
run.bat           # Windows        (same auto-venv logic)
```

Or manually:

```bash
python main.py
```

## Prompt format

The editor exports JSON accepted directly by the Ideogram 4 API:

```json
{
  "high_level_description": "A product poster for a smartwatch",
  "style_description": "Clean minimal background, soft shadows",
  "compositional_deconstruction": {
    "background": "Soft grey gradient",
    "elements": [
      {
        "type": "obj",
        "bbox": [100, 200, 800, 800],
        "desc": "Smartwatch hero shot",
        "color_palette": ["#1a1a2e", "#silver"]
      },
      {
        "type": "text",
        "bbox": [820, 100, 950, 900],
        "desc": "Product name",
        "text": "NOVA X1",
        "color_palette": ["#ffffff"]
      }
    ]
  }
}
```

`bbox` values are `[ymin, xmin, ymax, xmax]` in a 0–1000 relative coordinate space (resolution-independent).

## Development

```bash
pip install -r requirements-dev.txt
python -m pytest -q          # should show 50 passed
```

## Architecture

| File | Responsibility |
|------|----------------|
| `state.py` | Global mutable state + canvas geometry |
| `geometry.py` | Coordinate transforms, hit-test, mouse→canvas |
| `handlers.py` | Mouse FSM (press → drag → release) + keyboard |
| `toolbar.py` | Toolbar callbacks: add layer, new document, presets, i18n |
| `ui.py` | DPG window layout (3-column: layers \| canvas+fields \| properties) |
| `panels.py` | Layer list + properties panel |
| `draw.py` | Drawlist rendering |
| `prompt_io.py` | Save/load JSON, clipboard, overwrite confirmation |
| `history.py` | Undo/redo |
| `theme.py` | Global dark theme (Catppuccin Mocha) |
| `i18n.py` | RU/EN strings |
| `main.py` | Entry point + render loop |

## License

MIT — see [LICENSE](LICENSE).
