from app.utils.copyright import (
    get_copyright_expiry_year,
    is_public_domain,
    validate_copyright_for_sale,
)


class TestCopyrightUtils:
    """Copyright utility tests: normal, boundary, exception cases."""

    # --- Normal cases ---
    def test_beethoven_public_domain(self):
        assert is_public_domain(1827) is True  # 1827 + 50 = 1877 < 2026

    def test_modern_protected(self):
        assert is_public_domain(2000) is False  # 2000 + 50 = 2050 > 2026

    def test_expiry_year(self):
        assert get_copyright_expiry_year(1827) == 1877

    def test_validate_public_domain(self):
        ok, msg = validate_copyright_for_sale("public_domain")
        assert ok is True

    def test_validate_licensed(self):
        ok, msg = validate_copyright_for_sale("licensed")
        assert ok is True

    def test_validate_user_only(self):
        ok, msg = validate_copyright_for_sale("user_only")
        assert ok is False

    def test_validate_unknown_with_public_domain_death_year(self):
        ok, msg = validate_copyright_for_sale("unknown", death_year=1827, current_year=2026)
        assert ok is True

    def test_validate_unknown_no_death_year(self):
        ok, msg = validate_copyright_for_sale("unknown")
        assert ok is False

    # --- Boundary cases ---
    def test_exactly_50_years(self):
        """death_year + 50 = current_year — NOT public domain."""
        assert is_public_domain(1976, current_year=2026) is False

    def test_51_years(self):
        """death_year + 50 < current_year — public domain."""
        assert is_public_domain(1975, current_year=2026) is True

    def test_no_death_year(self):
        assert is_public_domain(None) is False

    def test_death_year_zero(self):
        """Ancient composer."""
        assert is_public_domain(0, current_year=2026) is True

    def test_death_year_negative(self):
        """BCE composer."""
        assert is_public_domain(-500, current_year=2026) is True

    # --- Exception cases ---
    def test_validate_unknown_protected_death_year(self):
        ok, msg = validate_copyright_for_sale("unknown", death_year=2000, current_year=2026)
        assert ok is False
        assert "unknown" in msg.lower() or "protected" in msg.lower()
