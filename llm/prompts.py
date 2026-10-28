"""Prompt templates and builders."""


def build_analyst_prompt(country_name: str, user_message: str) -> tuple[str, str]:
    """Build prompt for the analyst step: parse user request into structured JSON."""
    system_prompt = (
        f"Ты - аналитик хорошо разбирающийся в туристической отрасли страны – {country_name}. "
        f"Проанализируй следующий запрос от клиента – {user_message} "
        f"и напиши следующую разметку JSON:\n"
        f"{{\n"
        f'  "country": страна из запроса пользователя,\n'
        f'  "region": значение,\n'
        f'  "category": значение,\n'
        f'  "preferences": значение,\n'
        f'  "extraCountry": значение, если в запросе есть упоминание про другую страну\n'
        f"}}\n"
        f"Если значений несколько, кроме страны, то в виде массива перечисли."
    )
    user_prompt = (
        f"Страна: {country_name}\n"
        f"Запрос пользователя: {user_message}"
    )
    return system_prompt, user_prompt


def build_travel_expert_prompt(json_data: str) -> tuple[str, str]:
    """Build prompt for the travel expert step: generate hotel list from analyst JSON."""
    system_prompt = (
        "Ты — тревел-эксперт. Возвращай ответ строго в формате JSON."
    )
    user_prompt = (
        f"Ты – тревел-эксперт. Дай список из 2-3 отелей по каждому региону в соответствии со следующими условиями:\n"
        f"{json_data}\n"
        f"Для каждого отеля напиши описание, преимущества, нюансы, на что стоит обратить внимание, для какого отдыха подойдет.\n"
        f"*Если не указан регион предложи по 2-3 отеля в 3-4 разных регионах страны с указанием особенностей региона.\n"
        f"Ответ дай в разметке JSON:\n"
        f"{{\n"
        f'  "hotelList": [\n'
        f'    {{\n'
        f'      "region": ...\n'
        f'      "hotels": [\n'
        f'        {{\n'
        f'          "hotel": ...\n'
        f'          "description": ...\n'
        f'          "advantages": ...\n'
        f'          "nuance": ...\n'
        f'          "kindOfLeisure": ...\n'
        f"        }}\n"
        f"      ]\n"
        f"    }}\n"
        f"  ],\n"
        f'  "travelRecommendation": ...\n'
        f"}}\n"
        f"Ответ дай без воды, по делу, кратко."
    )
    return system_prompt, user_prompt
