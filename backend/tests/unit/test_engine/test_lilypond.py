import pytest

from app.engine.music.lilypond import LilyPondError, render_pdf, render_png


class TestLilyPond:
    """LilyPond rendering tests: normal, boundary, exception cases."""

    # --- Exception cases (LilyPond likely not installed in test env) ---
    def test_render_pdf_nonexistent_file(self, tmp_path):
        with pytest.raises(LilyPondError, match="file not found"):
            render_pdf(tmp_path / "nonexistent.ly")

    def test_render_png_nonexistent_file(self, tmp_path):
        with pytest.raises(LilyPondError, match="file not found"):
            render_png(tmp_path / "nonexistent.ly")

    def test_render_png_invalid_dpi_low(self, tmp_path):
        ly_path = tmp_path / "test.ly"
        ly_path.write_text("{ c' }")
        with pytest.raises(LilyPondError, match="DPI must be"):
            render_png(ly_path, dpi=10)

    def test_render_png_invalid_dpi_high(self, tmp_path):
        ly_path = tmp_path / "test.ly"
        ly_path.write_text("{ c' }")
        with pytest.raises(LilyPondError, match="DPI must be"):
            render_png(ly_path, dpi=1000)

    # --- Boundary: DPI limits ---
    def test_dpi_boundary_72(self, tmp_path):
        """DPI=72 is minimum valid — should not raise DPI error."""
        ly_path = tmp_path / "test.ly"
        ly_path.write_text("{ c' }")
        # May raise LilyPondError for "not installed", but NOT for DPI
        try:
            render_png(ly_path, dpi=72)
        except LilyPondError as e:
            assert "DPI" not in str(e)

    def test_dpi_boundary_600(self, tmp_path):
        """DPI=600 is maximum valid — should not raise DPI error."""
        ly_path = tmp_path / "test.ly"
        ly_path.write_text("{ c' }")
        try:
            render_png(ly_path, dpi=600)
        except LilyPondError as e:
            assert "DPI" not in str(e)
