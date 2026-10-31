"""Prompt templates and builders."""

import json


def build_analyst_prompt(user_message: str) -> str:
    """Build system prompt for the analyst step.

    The model will return JSON matching AnalystResponse schema.
    """
    return (
        f"Ты — аналитик туристической отрасли. "
        f"Клиент прислал запрос: {user_message}\n\n"
        f"Извлеки из запроса следующие параметры и верни в формате JSON:\n"
        f"- country: название страны (обязательно)\n"
        f"- region: список курортов/регионов (если есть в запросе, иначе пустой массив)\n"
        f"- category: список звездности отелей (если есть в запросе, иначе пустой массив)\n"
        f"- preferences: список предпочтений по отелю (если есть в запросе, иначе пустой массив)\n\n"
        f"Верни ТОЛЬКО JSON-объект, без пояснений и комментариев."
    )


def build_travel_expert_prompt(country_name: str, analyst_json: str) -> str:
    """Build system prompt for the travel expert step.

    The model will return JSON matching TravelExpertResponse schema.
    """
    user_prompt_text = build_travel_expert_user_prompt(analyst_json)

    return (
        "Ты – тревел-эксперт.\n"
        "Составь список из 5 отелей по запросу клиента:\n"
        f"{user_prompt_text}\n"
        "Для каждого отеля напиши:\n"
        "1. Название отеля (hotel)\n"
        "2. Описание (до 200 символов) (description)\n"
        "3. Количество звезд (число) (category)\n"
        "4. Преимущества, укажи, что соответствует preferences из user_prompt (до 300 символов) (advantages)\n"
        "5. Нюансы, на что стоит обратить внимание (до 150 символов) (nuance)\n"
        "6. Для какого отдыха подойдет (до 100 символов) (kindOfLeisure)\n"
        "Отели строго в указанных, регионах\n"
        "Если не указан регион предложи по 2-3 отеля в 3 разных регионах страны согласно критериям из запроса.\n"
        "В travelRecommendation напиши рекомендации времени отдыха в выбранной стране, максимально 200 символов.\n"
        "Верни ТОЛЬКО JSON-объект без пояснений и комментариев."
    )


def build_travel_expert_user_prompt(analyst_json: str) -> str:
    """Build user prompt for the travel expert step from analyst JSON.

    Parses the JSON and constructs a natural-language query about hotels.
    """
    country = ""
    region = []
    category = []
    preferences = []

    try:
        data = json.loads(analyst_json)
        country = data.get("country", "")
        region = data.get("region") or []
        category = data.get("category") or []
        preferences = data.get("preferences") or []
    except (json.JSONDecodeError, TypeError):
        pass

    region_phrase = ""
    if isinstance(region, list) and region:
        if len(region) == 1:
            region_phrase = f"в регионе {region[0]}"
        else:
            region_str = ", ".join(region)
            region_phrase = f"в регионах {region_str}"
    elif isinstance(region, str) and region:
        region_phrase = f"в регионе {region}"

    category_str = ""
    if isinstance(category, list):
        category_str = ", ".join(str(c) for c in category)
    else:
        category_str = str(category) if category else ""
    category_phrase = f"{category_str} звезд " if category_str else ""

    preferences_str = ""
    if isinstance(preferences, list):
        preferences_str = ", ".join(preferences)
    else:
        preferences_str = str(preferences) if preferences else ""

    user_prompt = (
        f"Какие отели {category_phrase}рекомендуешь для отдыха "
        f"в стране {country} {region_phrase}. "
        f"Мои предпочтения: {preferences_str}"
    )

    return " ".join(user_prompt.split())
