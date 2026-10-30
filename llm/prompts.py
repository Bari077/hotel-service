"""Prompt templates and builders."""


def build_analyst_prompt(country_name: str, user_message: str) -> str:
    """Build system prompt for the analyst step.

    The model will return JSON matching AnalystResponse schema.
    """
    return (
        f"Ты — аналитик туристической отрасли страны {country_name}. "
        f"Клиент прислал запрос: {user_message}\n\n"
        f"Извлеки из запроса следующие параметры и верни в формате JSON:\n"
        f"- country: название страны\n"
        f"- region: список курортов/регионов (если есть в запросе, иначе пустой массив)\n"
        f"- category: список звездности отелей (если есть в запросе, иначе пустой массив)\n"
        f"- preferences: список предпочтений по отелю (если есть в запросе, иначе пустой массив)\n\n"
        f"Верни ТОЛЬКО JSON-объект, без пояснений и комментариев."
    )


def build_travel_expert_prompt(analyst_json: str) -> str:
    """Build system prompt for the travel expert step.

    The model will return JSON matching TravelExpertResponse schema.
    """
    return (
        "Ты — тревел-эксперт. Сравнивай отели и формируй рекомендации.\n\n"
        f"Данные запроса клиента:\n{analyst_json}\n\n"
        "Составь список из 5 отелей в 2-3 регионах страны. "
        "Для каждого отеля напиши:\n"
        "1. Название отеля (hotel)\n"
        "2. Описание (до 200 символов)\n"
        "3. Количество звёзд (число 1-5)\n"
        "4. Преимущества (до 300 символов)\n"
        "5. Нюансы (до 150 символов)\n"
        "6. Для какого отдыха подойдёт (kindOfLeisure, до 100 символов)\n\n"
        "В travelRecommendation напиши рекомендации по лучшему времени для отдыха.\n\n"
        "Верни ТОЛЬКО JSON-объект без пояснений и комментариев."
    )
