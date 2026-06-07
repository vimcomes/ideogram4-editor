"""Tests for i18n module."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import i18n


def setup_function():
    i18n.set_lang("ru")


def test_t_returns_string_for_known_key():
    assert i18n.t("status_ready") == "Готов."


def test_t_returns_bracket_key_for_unknown():
    assert i18n.t("nonexistent_key_xyz") == "[nonexistent_key_xyz]"


def test_t_format_substitution():
    result = i18n.t("status_undo_done", count=5)
    assert "5" in result


def test_t_format_opened():
    result = i18n.t("status_opened", name="file.json", count=3)
    assert "file.json" in result
    assert "3" in result


def test_t_format_missing_kwarg_does_not_raise():
    # If a required kwarg is missing, t() should not raise — returns partial or raw
    result = i18n.t("status_opened")
    assert isinstance(result, str)


def test_set_lang_switches_to_en():
    i18n.set_lang("en")
    assert i18n.t("status_ready") == "Ready."
    assert i18n.t("panel_layers_title") == "Layers"


def test_set_lang_back_to_ru():
    i18n.set_lang("en")
    i18n.set_lang("ru")
    assert i18n.t("panel_layers_title") == "Слои"


def test_set_lang_ignores_unknown():
    i18n.set_lang("ru")
    i18n.set_lang("zz")  # unknown — should keep current lang
    assert i18n.t("status_ready") == "Готов."


def test_get_lang_reflects_current():
    i18n.set_lang("en")
    assert i18n.get_lang() == "en"
    i18n.set_lang("ru")
    assert i18n.get_lang() == "ru"


def test_all_ru_keys_present_in_en():
    ru_keys = set(i18n._STRINGS["ru"].keys())
    en_keys = set(i18n._STRINGS["en"].keys())
    missing = ru_keys - en_keys
    assert not missing, f"EN is missing keys: {missing}"


def test_all_en_keys_present_in_ru():
    ru_keys = set(i18n._STRINGS["ru"].keys())
    en_keys = set(i18n._STRINGS["en"].keys())
    missing = en_keys - ru_keys
    assert not missing, f"RU is missing keys: {missing}"


def test_available_langs_contains_ru_and_en():
    assert "ru" in i18n.AVAILABLE_LANGS
    assert "en" in i18n.AVAILABLE_LANGS


def test_canvas_draw_hint_with_mode():
    i18n.set_lang("en")
    result = i18n.t("canvas_draw_hint", mode="text")
    assert "text" in result

    i18n.set_lang("ru")
    result = i18n.t("canvas_draw_hint", mode="obj")
    assert "obj" in result
