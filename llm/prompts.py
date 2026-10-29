"""Prompt templates and builders."""

import json


def build_analyst_prompt(country_name: str, user_message: str) -> str:
    """Build system prompt for the analyst step."""
    return (
        f"Ты - аналитик, хорошо разбирающийся в туристической отрасли страны – {country_name}. "
        f"Проанализируй следующий запрос от клиента – ({user_message}) "
        f"и напиши следующую разметку JSON в строгом соответствии с форматом: "
        f"{{ "
        f'"country" : "{country_name}", '
        f'"region": подставь курорт, если есть в запросе пользователя. Если нет - пустой массив'
        f'"category": запрашиваемая пользователем звездность отеля, если есть в запросе. Если нет - пустой массив'
        f'"preferences": предпочтения по отелю из запроса пользователя '
        f"}} "
        f"Если значений несколько, кроме страны, то в виде массива перечисли их. "
        f"Не добавляй в JSON никаких пояснений, комментариев или лишних полей."
    )


def build_travel_expert_prompt(json_data: str) -> str:
    """Build system prompt for the travel expert step."""
    user_prompt_text = build_travel_expert_user_prompt(json_data)
    return (
        "Ты – тревел-эксперт. Ответ возвращай строго в указанной структуре JSON.\n"
        "Составь список из 5 отелей по запросу клиента:\n"
        f"{user_prompt_text}\n"
        "Для каждого отеля напиши:\n"
        "1. Название отеля (hotel)\n"
        "2. Описание (до 200 символов) (description)\n"
        "3. Количество звезд (число) (category)\n"
        "4. Преимущества, укажи, что соответствует preferences из user_prompt (до 300 символов) (advantages)\n"
        "5. Нюансы, на что стоит обратить внимание (до 150 символов) (nuance)\n"
        "6. Для какого отдыха подойдет (до 100 символов) (kindOfLeasure)\n"
        "Не предлагай отели в регионах, находящихся далее чем на 60 км от запрошенных пользователем\n"
        "*Если не указан регион предложи по 2-3 отеля в 3 разных регионах страны согласно критериям из запроса.\n"
        "В travelRecommendation напиши рекомендации времени отдыха в выбранной стране, максимально 200 символов.\n"
        "Структура JSON:\n"
        "{\n"
        '  "hotelList": [\n'
        '    {\n'
        '      "region": ...\n'
        '      "hotels": [\n'
        '        {\n'
        '          "hotel": ...\n'
        '          "category": ...\n'
        '          "description": ...\n'
        '          "advantages": ...\n'
        '          "nuance": ...\n'
        '          "kindOfLeasure": ...\n'
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ],\n"
        '  "travelRecommendation": ...\n'
        "}\n"
    )


def build_travel_expert_user_prompt(json_data: str) -> str:
    """Build user prompt for the travel expert step from analyst JSON.

    Parses the JSON and constructs a natural-language query about hotels.
    """
    data = json.loads(json_data)

    country = data.get("country", "неизвестной стране")

    region = data.get("region") or []
    region_phrase = ""
    if isinstance(region, list) and region:
        if len(region) == 1:
            region_phrase = f"в регионе {region[0]}"
        else:
            region_str = ", ".join(region)
            region_phrase = f"в регионах {region_str}"
    elif isinstance(region, str) and region:
        region_phrase = f"в регионе {region}"

    category = data.get("category") or []
    if isinstance(category, list):
        category_str = ", ".join(category)
    else:
        category_str = str(category)
    category_phrase = f"{category_str} звезд " if category_str else ""

    preferences = data.get("preferences") or []
    if isinstance(preferences, list):
        preferences_str = ", ".join(preferences)
    else:
        preferences_str = str(preferences)

    user_prompt = (
        f"Какие отели {category_phrase}рекомендуешь для отдыха "
        f"в стране {country} {region_phrase}. "
        f"Мои предпочтения: {preferences_str}"
    )

    return " ".join(user_prompt.split())
