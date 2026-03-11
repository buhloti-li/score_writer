import tempfile
from pathlib import Path

import pytest
from PIL import Image

from app.engine.omr.preprocessor import (
    MAX_FILE_SIZE,
    PreprocessorError,
    binarize_image,
    preprocess_image,
    preprocess_to_bytes,
    validate_image,
)


def _create_test_image(path: Path, size=(200, 300), color="white"):
    img = Image.new("RGB", size, color)
    img.save(str(path))


class TestImagePreprocessor:
    """Image preprocessor tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    def test_validate_valid_png(self, tmp_path):
        img_path = tmp_path / "test.png"
        _create_test_image(img_path)
        result = validate_image(img_path)
        assert result == img_path

    def test_validate_valid_jpg(self, tmp_path):
        img_path = tmp_path / "test.jpg"
        _create_test_image(img_path)
        result = validate_image(img_path)
        assert result == img_path

    def test_preprocess_image(self, tmp_path):
        img_path = tmp_path / "test.png"
        _create_test_image(img_path, color="gray")
        result = preprocess_image(img_path)
        assert result.mode == "L"  # grayscale

    def test_preprocess_to_bytes(self, tmp_path):
        img_path = tmp_path / "test.png"
        _create_test_image(img_path)
        data = preprocess_to_bytes(img_path)
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_binarize_image(self, tmp_path):
        img_path = tmp_path / "test.png"
        _create_test_image(img_path, color="gray")
        gray = preprocess_image(img_path)
        binary = binarize_image(gray, threshold=128)
        assert binary.mode == "1"

    # --- Boundary cases ---
    def test_binarize_threshold_zero(self, tmp_path):
        img_path = tmp_path / "test.png"
        _create_test_image(img_path)
        gray = preprocess_image(img_path)
        binary = binarize_image(gray, threshold=0)
        assert binary.mode == "1"

    def test_binarize_threshold_255(self, tmp_path):
        img_path = tmp_path / "test.png"
        _create_test_image(img_path)
        gray = preprocess_image(img_path)
        binary = binarize_image(gray, threshold=255)
        assert binary.mode == "1"

    def test_validate_supported_formats(self, tmp_path):
        for ext in [".jpg", ".jpeg", ".png", ".tiff", ".bmp"]:
            img_path = tmp_path / f"test{ext}"
            if ext == ".tiff":
                Image.new("RGB", (10, 10)).save(str(img_path), format="TIFF")
            elif ext == ".bmp":
                Image.new("RGB", (10, 10)).save(str(img_path), format="BMP")
            else:
                _create_test_image(img_path)
            validate_image(img_path)  # should not raise

    # --- Exception cases ---
    def test_validate_nonexistent_file(self):
        with pytest.raises(PreprocessorError, match="File not found"):
            validate_image("/nonexistent/path.png")

    def test_validate_unsupported_format(self, tmp_path):
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("not an image")
        with pytest.raises(PreprocessorError, match="Unsupported format"):
            validate_image(txt_path)

    def test_validate_file_too_large(self, tmp_path):
        big_path = tmp_path / "big.png"
        big_path.write_bytes(b"0" * (MAX_FILE_SIZE + 1))
        with pytest.raises(PreprocessorError, match="File too large"):
            validate_image(big_path)

    def test_binarize_invalid_threshold_negative(self, tmp_path):
        img_path = tmp_path / "test.png"
        _create_test_image(img_path)
        gray = preprocess_image(img_path)
        with pytest.raises(PreprocessorError, match="Threshold must be"):
            binarize_image(gray, threshold=-1)

    def test_binarize_invalid_threshold_too_high(self, tmp_path):
        img_path = tmp_path / "test.png"
        _create_test_image(img_path)
        gray = preprocess_image(img_path)
        with pytest.raises(PreprocessorError, match="Threshold must be"):
            binarize_image(gray, threshold=256)
