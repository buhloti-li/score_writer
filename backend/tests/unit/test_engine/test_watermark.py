import pytest
from PIL import Image

from app.engine.watermark import WatermarkError, add_image_watermark


def _create_test_image(path, size=(400, 600)):
    img = Image.new("RGB", size, "white")
    img.save(str(path))


class TestImageWatermark:
    """Watermark tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    def test_add_watermark(self, tmp_path):
        img_path = tmp_path / "input.png"
        out_path = tmp_path / "output.png"
        _create_test_image(img_path)
        result = add_image_watermark(img_path, out_path)
        assert result.exists()
        img = Image.open(result)
        assert img.size == (400, 600)

    def test_custom_text(self, tmp_path):
        img_path = tmp_path / "input.png"
        out_path = tmp_path / "output.png"
        _create_test_image(img_path)
        result = add_image_watermark(img_path, out_path, text="Custom Watermark")
        assert result.exists()

    def test_custom_opacity(self, tmp_path):
        img_path = tmp_path / "input.png"
        out_path = tmp_path / "output.png"
        _create_test_image(img_path)
        result = add_image_watermark(img_path, out_path, opacity=50)
        assert result.exists()

    # --- Boundary cases ---
    def test_opacity_zero(self, tmp_path):
        img_path = tmp_path / "input.png"
        out_path = tmp_path / "output.png"
        _create_test_image(img_path)
        result = add_image_watermark(img_path, out_path, opacity=0)
        assert result.exists()

    def test_opacity_max(self, tmp_path):
        img_path = tmp_path / "input.png"
        out_path = tmp_path / "output.png"
        _create_test_image(img_path)
        result = add_image_watermark(img_path, out_path, opacity=255)
        assert result.exists()

    def test_small_image(self, tmp_path):
        img_path = tmp_path / "small.png"
        out_path = tmp_path / "output.png"
        _create_test_image(img_path, size=(10, 10))
        result = add_image_watermark(img_path, out_path)
        assert result.exists()

    def test_output_dir_created(self, tmp_path):
        img_path = tmp_path / "input.png"
        out_path = tmp_path / "subdir" / "output.png"
        _create_test_image(img_path)
        result = add_image_watermark(img_path, out_path)
        assert result.exists()

    # --- Exception cases ---
    def test_nonexistent_input(self, tmp_path):
        with pytest.raises(WatermarkError, match="Image not found"):
            add_image_watermark("/nonexistent.png", tmp_path / "out.png")

    def test_invalid_opacity_negative(self, tmp_path):
        img_path = tmp_path / "input.png"
        _create_test_image(img_path)
        with pytest.raises(WatermarkError, match="Opacity must be"):
            add_image_watermark(img_path, tmp_path / "out.png", opacity=-1)

    def test_invalid_opacity_too_high(self, tmp_path):
        img_path = tmp_path / "input.png"
        _create_test_image(img_path)
        with pytest.raises(WatermarkError, match="Opacity must be"):
            add_image_watermark(img_path, tmp_path / "out.png", opacity=256)
