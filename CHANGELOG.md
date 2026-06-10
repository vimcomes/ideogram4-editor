# Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.2.1] — 2026-06-10

### Fixed
- **Native file dialogs** — replaced DearPyGui's built-in file dialog with native OS dialogs (GTK on Linux, Win32 on Windows, Cocoa on macOS) via `tkinter.filedialog`. Fixes clipboard paste crash (`X11: Failed to convert selection to string`) and broken path input in all three dialogs: open prompt, save prompt, underlay image. DPG dialog kept as automatic fallback if tkinter is unavailable.

---

## [0.2.0] — 2026-06-09

### Added
- **Color picker** — `◐` button next to every `color_palette` field (element and global style). Opens a visual wheel picker; selected hex is appended comma-separated to the field. Works on Windows (DejaVu-safe glyph, zero new dependencies).
- **Reference image underlay** — load a PNG/JPG as a semi-transparent reference under the canvas. Controls: opacity slider, stretch/crop fit modes, visibility toggle, add/remove. Editor-only state — never written to the prompt JSON.
- **Version label** — app version displayed in the window title bar (`v0.2.0`).

### Fixed
- Underlay panel always visible at the bottom of the left column (no scroll required).
- Color picker dialog wide enough to show the color preview swatch and OK/Cancel buttons without scrolling.

---

## [0.1.0] — 2026-06-08

### Added
- **Photo / Art style mode toggle** — switches between `style_description` key order for Ideogram 4 photo vs art prompts.
- **Example prompts** — `examples/` directory with `magazine_cover.json`, `scifi_poster.json`, `comfyui_arcade.json`.
- **Overwrite confirmation dialog** — shown when saving over an existing file.
- **Draggable horizontal splitter** — resize canvas vs fields area by dragging.
- **Dark theme** — consistent dark UI via DearPyGui theme.
- **Inline layer actions** — ↑ ↓ ✕ buttons directly in the layer list.
- **Collapsible style panel** — style description section can be collapsed.
- **RU/EN i18n** — full bilingual support, language switcher in toolbar.
- **Sub-fields for style description** — Aesthetics, Lighting, Camera, Artist, Extra.
- **Undo/redo** — Ctrl+Z / Ctrl+Y history.
- **Resolution presets** — dropdown with common Ideogram 4 aspect ratios.
- **Save/load JSON** — exports Ideogram 4 prompt format; load restores full session.
- Test suite (68 tests).

### Fixed
- Canvas sizing and mouse hit-testing for DearPyGui 2.3.1.
- Cross-platform font path; DejaVu-safe toolbar icons (Windows compatible).
- Bbox input fields widened to 2×2 layout.
- Undo drain prevented when Ctrl+Z held down.
- Undo history cleared on file open.
