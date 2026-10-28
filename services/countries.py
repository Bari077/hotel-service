"""Country ID to name mapping."""

COUNTRY_MAP: dict[int, str] = {
    1: "Турция",
    2: "Египет",
    3: "ОАЭ",
    4: "Тайланд",
    5: "Вьетнам",
    6: "Китай",
    7: "Мальдивы",
    8: "Шри-Ланка",
}


def get_country_name(country_id: int) -> str:
    """Return country name by ID, or None if not found."""
    return COUNTRY_MAP.get(country_id)
