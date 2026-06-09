"""Tests for colorwidget pure functions (GUI-free)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from colorwidget import rgb_to_hex, append_hex


class TestRgbToHex:
    def test_basic(self):
        assert rgb_to_hex([255, 0, 0]) == "#ff0000"

    def test_black(self):
        assert rgb_to_hex([0, 0, 0]) == "#000000"

    def test_white(self):
        assert rgb_to_hex([255, 255, 255]) == "#ffffff"

    def test_mid(self):
        assert rgb_to_hex([51, 153, 204]) == "#3399cc"

    def test_ignores_alpha(self):
        assert rgb_to_hex([255, 0, 0, 128]) == "#ff0000"


class TestAppendHex:
    def test_empty_string(self):
        assert append_hex("", "#aabbcc") == "#aabbcc"

    def test_existing_value(self):
        assert append_hex("#aabbcc", "#112233") == "#aabbcc, #112233"

    def test_trailing_comma(self):
        assert append_hex("#aabbcc, ", "#112233") == "#aabbcc, #112233"

    def test_trailing_comma_no_space(self):
        assert append_hex("#aabbcc,", "#112233") == "#aabbcc, #112233"

    def test_whitespace_only(self):
        assert append_hex("   ", "#aabbcc") == "#aabbcc"

    def test_multiple_existing(self):
        result = append_hex("#ff0000, #00ff00", "#0000ff")
        assert result == "#ff0000, #00ff00, #0000ff"
