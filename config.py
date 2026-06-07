"""config.py — constants and paths for Ideogram4 Layout Editor."""
import os

APP_DIR      = os.path.dirname(os.path.abspath(__file__))
PRESETS_FILE = os.path.join(APP_DIR, "presets", "resolutions.json")
PROMPTS_DIR  = os.path.join(APP_DIR, "prompts")

def _find_font() -> str:
    candidates = [
        os.path.join(APP_DIR, "assets", "fonts", "DejaVuSans.ttf"),  # bundled (cross-platform)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",            # Linux
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",                     # some Linux distros
        "C:/Windows/Fonts/DejaVuSans.ttf",                            # Windows (if installed)
        os.path.expanduser("~/Library/Fonts/DejaVuSans.ttf"),         # macOS user
        "/Library/Fonts/DejaVuSans.ttf",                              # macOS system
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    raise FileNotFoundError("DejaVuSans.ttf not found. Place it in assets/fonts/DejaVuSans.ttf")

FONT_PATH    = _find_font()

HANDLE      = 8
INIT_W      = 1400
INIT_H      = 860
MIN_AREA_PX = 100

os.makedirs(PROMPTS_DIR, exist_ok=True)
