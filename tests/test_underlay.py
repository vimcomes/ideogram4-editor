"""Tests for underlay pure functions (GUI-free)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from underlay import compute_uv


class TestComputeUvStretch:
    def test_stretch_always_full(self):
        assert compute_uv(800, 600, 400, 300, "stretch") == ((0.0, 0.0), (1.0, 1.0))

    def test_stretch_zero_dims(self):
        assert compute_uv(0, 0, 400, 300, "stretch") == ((0.0, 0.0), (1.0, 1.0))


class TestComputeUvCrop:
    def test_same_aspect(self):
        # identical aspect → no crop
        uv_min, uv_max = compute_uv(800, 600, 400, 300, "crop")
        assert uv_min == (0.0, 0.0)
        assert uv_max == (1.0, 1.0)

    def test_wide_image_crops_sides(self):
        # image 1600×600 (ar=2.67), canvas 400×300 (ar=1.33)
        # image is wider → crop left/right
        uv_min, uv_max = compute_uv(1600, 600, 400, 300, "crop")
        u0, v0 = uv_min
        u1, v1 = uv_max
        assert v0 == 0.0 and v1 == 1.0   # full height used
        assert u0 > 0.0 and u1 < 1.0     # sides cropped
        assert abs((u1 - u0) - 0.5) < 1e-9  # crop_w_uv = 1.33/2.67 ≈ 0.5

    def test_tall_image_crops_top_bottom(self):
        # image 400×1200 (ar=0.33), canvas 400×300 (ar=1.33)
        # image is taller → crop top/bottom
        uv_min, uv_max = compute_uv(400, 1200, 400, 300, "crop")
        u0, v0 = uv_min
        u1, v1 = uv_max
        assert u0 == 0.0 and u1 == 1.0   # full width used
        assert v0 > 0.0 and v1 < 1.0     # top/bottom cropped

    def test_square_image_portrait_canvas(self):
        # square image 500×500, portrait canvas 300×600 (ar=0.5)
        # image ar=1.0 > canvas ar=0.5 → crop sides
        uv_min, uv_max = compute_uv(500, 500, 300, 600, "crop")
        u0, v0 = uv_min
        u1, v1 = uv_max
        assert v0 == 0.0 and v1 == 1.0
        assert u0 > 0.0


class TestPromptHasNoUnderlay:
    """Ensure build_prompt never leaks underlay state into output JSON."""
    def test_no_underlay_keys(self):
        # Import without DPG by patching dpg before prompt_io loads it
        import types, unittest.mock as mock

        fake_dpg = types.ModuleType("dearpygui.dearpygui")
        fake_dpg.get_value = mock.Mock(return_value="")
        fake_dpg.does_item_exist = mock.Mock(return_value=False)

        import sys
        sys.modules.setdefault("dearpygui", types.ModuleType("dearpygui"))
        sys.modules["dearpygui.dearpygui"] = fake_dpg

        import importlib
        import state as st_mod
        # Reset underlay so test is self-contained
        st_mod.st["underlay"]["path"] = "/some/image.png"

        import prompt_io
        importlib.reload(prompt_io)  # pick up patched dpg

        result = prompt_io.build_prompt()
        top_keys = set(result.keys())
        assert "underlay" not in top_keys
        assert "underlay_path" not in top_keys
        assert top_keys == {"high_level_description", "style_description",
                            "compositional_deconstruction"}
