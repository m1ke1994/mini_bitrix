import re


ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PHONE_RE = re.compile(r"^\+?[0-9\s\-()]{7,24}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_phone_for_dedup(value) -> str:
    if value is None:
        return ""
    raw_phone = str(value).strip()
    if not raw_phone or ISO_DATE_RE.fullmatch(raw_phone):
        return ""
    if not PHONE_RE.fullmatch(raw_phone):
        return ""

    digits = re.sub(r"\D", "", raw_phone)
    if len(digits) < 7:
        return ""

    if len(digits) == 11 and digits.startswith("8"):
        digits = f"7{digits[1:]}"
    if len(digits) == 10:
        digits = f"7{digits}"
    return f"+{digits}"


def normalize_email(value) -> str:
    if value is None:
        return ""
    email = str(value).strip().lower()
    if not email:
        return ""
    if not EMAIL_RE.fullmatch(email):
        return ""
    return email


def normalize_phone(value):
    normalized = normalize_phone_for_dedup(value)
    return normalized or None

