"""config.py — constants and paths for Ideogram4 Layout Editor."""
import os

APP_DIR      = os.path.dirname(os.path.abspath(__file__))
PRESETS_FILE = os.path.join(APP_DIR, "presets", "resolutions.json")
PROMPTS_DIR  = os.path.join(APP_DIR, "prompts")
FONT_PATH    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

HANDLE      = 8
INIT_W      = 1400
INIT_H      = 860
MIN_AREA_PX = 100

os.makedirs(PROMPTS_DIR, exist_ok=True)
