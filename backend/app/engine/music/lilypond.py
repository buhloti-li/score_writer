import subprocess
from pathlib import Path


class LilyPondError(Exception):
    pass


def render_pdf(ly_path: str | Path, output_dir: str | Path | None = None) -> Path:
    ly_path = Path(ly_path)
    if not ly_path.exists():
        raise LilyPondError(f"LilyPond file not found: {ly_path}")

    if output_dir is None:
        output_dir = ly_path.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_stem = output_dir / ly_path.stem

    try:
        result = subprocess.run(
            ["lilypond", "--pdf", "-o", str(output_stem), str(ly_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        raise LilyPondError("LilyPond is not installed or not in PATH")
    except subprocess.TimeoutExpired:
        raise LilyPondError("LilyPond rendering timed out (120s)")

    pdf_path = output_stem.with_suffix(".pdf")
    if not pdf_path.exists():
        raise LilyPondError(f"LilyPond failed to produce PDF. stderr: {result.stderr}")

    return pdf_path


def render_png(ly_path: str | Path, output_dir: str | Path | None = None, dpi: int = 300) -> Path:
    ly_path = Path(ly_path)
    if not ly_path.exists():
        raise LilyPondError(f"LilyPond file not found: {ly_path}")

    if dpi < 72 or dpi > 600:
        raise LilyPondError(f"DPI must be between 72 and 600, got {dpi}")

    if output_dir is None:
        output_dir = ly_path.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_stem = output_dir / ly_path.stem

    try:
        result = subprocess.run(
            [
                "lilypond",
                "--png",
                f"-dresolution={dpi}",
                "-o",
                str(output_stem),
                str(ly_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        raise LilyPondError("LilyPond is not installed or not in PATH")
    except subprocess.TimeoutExpired:
        raise LilyPondError("LilyPond rendering timed out (120s)")

    png_path = output_stem.with_suffix(".png")
    if not png_path.exists():
        raise LilyPondError(f"LilyPond failed to produce PNG. stderr: {result.stderr}")

    return png_path


def check_lilypond_installed() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["lilypond", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            version = result.stdout.strip().split("\n")[0]
            return True, version
        return False, result.stderr
    except FileNotFoundError:
        return False, "LilyPond not found in PATH"
    except subprocess.TimeoutExpired:
        return False, "Timeout checking LilyPond version"
