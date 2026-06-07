"""i18n.py — internationalisation strings for RU/EN."""

_STRINGS: dict[str, dict[str, str]] = {
    "ru": {
        # App
        "app_title":               "Ideogram4 Layout Editor",
        # Toolbar
        "toolbar_resolution":      "Разрешение:",
        "toolbar_btn_new":         "□",
        "toolbar_btn_copy":        "❐",
        "toolbar_btn_open":        "△",
        "toolbar_btn_save":        "▽",
        "toolbar_btn_undo":        "↩",
        "toolbar_btn_add_text":    "⊕T",
        "toolbar_btn_add_obj":     "⊕O",
        "toolbar_btn_move_up":     "↑",
        "toolbar_btn_move_down":   "↓",
        "toolbar_btn_delete":      "✕",
        # Layer panel
        "panel_layers_title":      "Слои",
        # Properties panel
        "panel_props_title":       "Свойства слоя",
        "props_no_selection":      "← Выбери слой",
        "props_layer_title":       "Слой #{index}",
        "props_type_label":        "Тип:",
        "props_text_label":        "Текст:",
        "props_desc_label":        "Описание (desc):",
        "props_bbox_label":        "BBox  [ymin xmin ymax xmax]  0–1000:",
        "props_palette_label":     "Color palette (hex через запятую):",
        "layer_empty_label":       "—",
        # Fields (middle panel)
        "field_high_level":           "High-level description:",
        "field_style":                "Style description",
        "field_style_aesthetics":     "Aesthetics:",
        "field_style_lighting":       "Lighting:",
        "field_style_art_style":      "Art style:",
        "field_style_medium":         "Medium:",
        "field_style_palette":        "Color palette (hex через запятую):",
        "field_background":           "Background:",
        # File dialogs
        "dialog_open_title":       "Открыть промпт",
        "dialog_save_title":       "Сохранить промпт",
        "file_filter_all":         "Все файлы",
        "file_filter_json":        "JSON промпт",
        "file_filter_txt":         "TXT + JSON",
        # Status messages
        "status_initial":          "Ctrl+Z = undo  |  Esc = отмена режима рисования",
        "status_ready":            "Готов.",
        "status_new":              "Новый документ.",
        "status_draw_text":        "Нарисуй bbox для [text]  (Esc = отмена)",
        "status_draw_obj":         "Нарисуй bbox для [obj]  (Esc = отмена)",
        "status_undo_empty":       "Нечего отменять.",
        "status_undo_done":        "Undo  ({count} шагов в истории)",
        "status_copied":           "Скопировано в буфер  ({count} слоёв)",
        "status_no_file":          "Файл не выбран.",
        "status_opened":           "Открыт: {name}  ({count} слоёв)",
        "status_no_path":          "Путь не указан.",
        "status_saved":            "Сохранено → {path}",
        "status_error":            "Ошибка: {err}",
        "status_error_open":       "Ошибка открытия: {err}",
        "status_error_save":       "Ошибка сохранения: {err}",
        "error_json_not_in_txt":   "JSON не найден в .txt файле",
        # Canvas hints (drawn on drawlist)
        "canvas_draw_hint":        "Рисуй bbox [{mode}]  (Esc = отмена)",
    },
    "en": {
        # App
        "app_title":               "Ideogram4 Layout Editor",
        # Toolbar
        "toolbar_resolution":      "Resolution:",
        "toolbar_btn_new":         "□",
        "toolbar_btn_copy":        "❐",
        "toolbar_btn_open":        "△",
        "toolbar_btn_save":        "▽",
        "toolbar_btn_undo":        "↩",
        "toolbar_btn_add_text":    "⊕T",
        "toolbar_btn_add_obj":     "⊕O",
        "toolbar_btn_move_up":     "↑",
        "toolbar_btn_move_down":   "↓",
        "toolbar_btn_delete":      "✕",
        # Layer panel
        "panel_layers_title":      "Layers",
        # Properties panel
        "panel_props_title":       "Layer properties",
        "props_no_selection":      "← Select a layer",
        "props_layer_title":       "Layer #{index}",
        "props_type_label":        "Type:",
        "props_text_label":        "Text:",
        "props_desc_label":        "Description (desc):",
        "props_bbox_label":        "BBox  [ymin xmin ymax xmax]  0–1000:",
        "props_palette_label":     "Color palette (hex, comma-separated):",
        "layer_empty_label":       "—",
        # Fields (middle panel)
        "field_high_level":           "High-level description:",
        "field_style":                "Style description",
        "field_style_aesthetics":     "Aesthetics:",
        "field_style_lighting":       "Lighting:",
        "field_style_art_style":      "Art style:",
        "field_style_medium":         "Medium:",
        "field_style_palette":        "Color palette (hex, comma-separated):",
        "field_background":           "Background:",
        # File dialogs
        "dialog_open_title":       "Open prompt",
        "dialog_save_title":       "Save prompt",
        "file_filter_all":         "All files",
        "file_filter_json":        "JSON prompt",
        "file_filter_txt":         "TXT + JSON",
        # Status messages
        "status_initial":          "Ctrl+Z = undo  |  Esc = cancel draw mode",
        "status_ready":            "Ready.",
        "status_new":              "New document.",
        "status_draw_text":        "Draw bbox for [text]  (Esc = cancel)",
        "status_draw_obj":         "Draw bbox for [obj]  (Esc = cancel)",
        "status_undo_empty":       "Nothing to undo.",
        "status_undo_done":        "Undo  ({count} steps in history)",
        "status_copied":           "Copied to clipboard  ({count} layers)",
        "status_no_file":          "No file selected.",
        "status_opened":           "Opened: {name}  ({count} layers)",
        "status_no_path":          "No path specified.",
        "status_saved":            "Saved → {path}",
        "status_error":            "Error: {err}",
        "status_error_open":       "Error opening: {err}",
        "status_error_save":       "Error saving: {err}",
        "error_json_not_in_txt":   "JSON not found in .txt file",
        # Canvas hints (drawn on drawlist)
        "canvas_draw_hint":        "Draw bbox [{mode}]  (Esc = cancel)",
    },
}

AVAILABLE_LANGS = list(_STRINGS.keys())

_lang = "en"


def set_lang(lang: str) -> None:
    global _lang
    if lang in _STRINGS:
        _lang = lang


def get_lang() -> str:
    return _lang


def t(key: str, **kwargs: object) -> str:
    """Return translated string for *key* in the current language."""
    s = _STRINGS.get(_lang, _STRINGS["ru"]).get(key, f"[{key}]")
    if kwargs:
        try:
            s = s.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return s
