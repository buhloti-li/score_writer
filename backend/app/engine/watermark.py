import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class WatermarkError(Exception):
    pass


def add_image_watermark(
    image_path: str | Path,
    output_path: str | Path,
    text: str = "PREVIEW - scorewriter.com",
    opacity: int = 80,
    font_size: int = 36,
    angle: int = -30,
) -> Path:
    image_path = Path(image_path)
    output_path = Path(output_path)

    if not image_path.exists():
        raise WatermarkError(f"Image not found: {image_path}")
    if opacity < 0 or opacity > 255:
        raise WatermarkError(f"Opacity must be 0-255, got {opacity}")

    base = Image.open(image_path).convert("RGBA")

    # Create watermark layer
    watermark = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()

    # Tile watermark text across the image
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    step_x = text_width + 100
    step_y = text_height + 150

    for y in range(-base.height, base.height * 2, step_y):
        for x in range(-base.width, base.width * 2, step_x):
            draw.text((x, y), text, fill=(128, 128, 128, opacity), font=font)

    watermark = watermark.rotate(angle, expand=False, center=(base.width // 2, base.height // 2))

    # Crop watermark to original size
    watermark = watermark.crop((0, 0, base.width, base.height))

    result = Image.alpha_composite(base, watermark)
    result = result.convert("RGB")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(str(output_path))

    return output_path


def add_pdf_watermark(
    pdf_path: str | Path,
    output_path: str | Path,
    text: str = "PREVIEW - scorewriter.com",
) -> Path:
    from io import BytesIO

    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    if not pdf_path.exists():
        raise WatermarkError(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()

    for page in reader.pages:
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)

        # Create watermark PDF in memory
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))
        c.setFont("Helvetica", 40)
        c.setFillAlpha(0.15)
        c.saveState()
        c.translate(page_width / 2, page_height / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
        c.restoreState()
        c.save()

        packet.seek(0)
        watermark_page = PdfReader(packet).pages[0]

        page.merge_page(watermark_page)
        writer.add_page(page)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(output_path), "wb") as f:
        writer.write(f)

    return output_path
