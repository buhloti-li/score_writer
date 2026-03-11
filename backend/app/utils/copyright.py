from datetime import datetime, timezone


def is_public_domain(death_year: int | None, current_year: int | None = None) -> bool:
    if death_year is None:
        return False
    if current_year is None:
        current_year = datetime.now(timezone.utc).year
    return (death_year + 50) < current_year


def get_copyright_expiry_year(death_year: int) -> int:
    return death_year + 50


def validate_copyright_for_sale(
    copyright_status: str,
    death_year: int | None = None,
    current_year: int | None = None,
) -> tuple[bool, str]:
    if copyright_status == "public_domain":
        return True, "Public domain work, safe to sell."
    if copyright_status == "licensed":
        return True, "Licensed work, check license terms."
    if copyright_status == "user_only":
        return False, "User-commissioned work, cannot be publicly sold."
    # Unknown status — check death year
    if death_year is not None and is_public_domain(death_year, current_year):
        return True, "Composer death year indicates public domain."
    return False, "Copyright status unknown or work is still protected."
