"""Prompt templates and builders."""


def build_prompt(country_id: int, user_message: str) -> str:
    """Build a system + user prompt for GigaChat based on country and user input."""
    system_prompt = (
        "Ты — помощник сервиса hotel-service. "
        "Отвечай на русском языке, кратко и по делу. Формат ответа - список не более 5 отелей"
    )
    user_prompt = (
        f"Страна ID: {country_id}\n"
        f"Запрос пользователя: {user_message}"
    )
    return system_prompt, user_prompt
