import io
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


class PreprocessorError(Exception):
    pass


MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"}


def validate_image(file_path: str | Path) -> Path:
    path = Path(file_path)
    if not path.exists():
        raise PreprocessorError(f"File not found: {path}")
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise PreprocessorError(
            f"Unsupported format: {path.suffix}. Supported: {SUPPORTED_FORMATS}"
        )
    if path.stat().st_size > MAX_FILE_SIZE:
        raise PreprocessorError(f"File too large: {path.stat().st_size} bytes (max {MAX_FILE_SIZE})")
    return path


def preprocess_image(file_path: str | Path) -> Image.Image:
    path = validate_image(file_path)
    img = Image.open(path)

    # Convert to grayscale
    img = ImageOps.grayscale(img)

    # Auto contrast
    img = ImageOps.autocontrast(img, cutoff=1)

    # Light sharpen
    img = img.filter(ImageFilter.SHARPEN)

    return img


def preprocess_to_bytes(file_path: str | Path) -> bytes:
    img = preprocess_image(file_path)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def binarize_image(img: Image.Image, threshold: int = 128) -> Image.Image:
    if threshold < 0 or threshold > 255:
        raise PreprocessorError(f"Threshold must be 0-255, got {threshold}")
    return img.point(lambda x: 255 if x > threshold else 0, "1")
