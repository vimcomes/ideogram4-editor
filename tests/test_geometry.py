"""Tests for geometry coordinate transforms (no DPG required)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Patch DPG before importing geometry so the module can be imported headless
from unittest.mock import MagicMock
sys.modules["dearpygui"] = MagicMock()
sys.modules["dearpygui.dearpygui"] = MagicMock()

import state
import geometry


def _set_canvas(w: int, h: int, img_w: int = 1000, img_h: int = 1000):
    state.g_dl_w = w
    state.g_dl_h = h
    state.st["img_w"] = img_w
    state.st["img_h"] = img_h


# ── canvas_dims ────────────────────────────────────────────────────────────────

def test_canvas_dims_square_image_fits_in_square_canvas():
    _set_canvas(500, 500, img_w=1000, img_h=1000)
    cw, ch, scale = geometry.canvas_dims()
    assert cw == ch
    assert scale == pytest_approx(496 / 1000, rel=0.01)


def test_canvas_dims_wide_image_constrained_by_width():
    _set_canvas(400, 400, img_w=2000, img_h=1000)
    cw, ch, scale = geometry.canvas_dims()
    assert cw <= 396  # avail_w = 400 - 4
    assert ch <= 396
    # scale constrained by width: 396/2000
    assert abs(scale - 396 / 2000) < 0.01


def test_canvas_dims_tall_image_constrained_by_height():
    _set_canvas(400, 400, img_w=1000, img_h=2000)
    cw, ch, scale = geometry.canvas_dims()
    assert ch <= 396
    assert abs(scale - 396 / 2000) < 0.01


def test_canvas_dims_minimum_size():
    _set_canvas(50, 50)  # very small canvas
    cw, ch, scale = geometry.canvas_dims()
    assert cw > 0
    assert ch > 0


# ── bbox_to_rel / rel_to_bbox roundtrip ───────────────────────────────────────

def test_bbox_to_rel_full_coverage():
    _set_canvas(500, 500, 1000, 1000)
    x0, y0, x1, y1 = geometry.bbox_to_rel([0, 0, 1000, 1000])
    assert x0 == 0 and y0 == 0
    assert x1 > 0 and y1 > 0


def test_bbox_to_rel_center():
    _set_canvas(500, 500, 1000, 1000)
    cw, ch, _ = geometry.canvas_dims()
    x0, y0, x1, y1 = geometry.bbox_to_rel([250, 250, 750, 750])
    assert abs(x0 - cw * 0.25) < 2
    assert abs(y0 - ch * 0.25) < 2
    assert abs(x1 - cw * 0.75) < 2
    assert abs(y1 - ch * 0.75) < 2


def test_rel_to_bbox_clamps_to_1000():
    _set_canvas(500, 500, 1000, 1000)
    cw, ch, _ = geometry.canvas_dims()
    bbox = geometry.rel_to_bbox(0, 0, cw + 999, ch + 999)
    assert all(0 <= v <= 1000 for v in bbox)


def test_rel_to_bbox_order_independent():
    _set_canvas(500, 500, 1000, 1000)
    cw, ch, _ = geometry.canvas_dims()
    # Drawing from bottom-right to top-left
    a = geometry.rel_to_bbox(cw * 0.75, ch * 0.75, cw * 0.25, ch * 0.25)
    b = geometry.rel_to_bbox(cw * 0.25, ch * 0.25, cw * 0.75, ch * 0.75)
    assert a == b  # both should produce same [ymin, xmin, ymax, xmax]


def test_bbox_roundtrip():
    _set_canvas(600, 800, img_w=1168, img_h=1712)
    original = [100, 200, 400, 800]
    cw, ch, _ = geometry.canvas_dims()
    x0, y0, x1, y1 = geometry.bbox_to_rel(original)
    recovered = geometry.rel_to_bbox(x0, y0, x1, y1)
    # Allow ±2 rounding error per coordinate
    for a, b in zip(original, recovered):
        assert abs(a - b) <= 2, f"roundtrip mismatch: {original} → {recovered}"


# ── pytest_approx helper (stdlib only, no pytest dependency needed for the value) ─
def pytest_approx(val, rel=1e-6):
    """Very simple approx wrapper that returns val (tests use abs())."""
    return val
