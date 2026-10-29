"""Core service implementations."""

import json
import os
import logging

from services.countries import get_country_name
from cache.cache import cache_get, cache_set
from llm.model import chat_completion
from llm.prompts import build_analyst_prompt, build_travel_expert_prompt
from utils.json_parser import extract_json

logger = logging.getLogger("hotel-service")


def _parse_analyst_response(response: str) -> dict:
    """Extract JSON from analyst's response."""
    response = response.strip()
    start = response.find("{")
    end = response.rfind("}") + 1
    if start != -1 and end > start:
        response = response[start:end]
    return json.loads(response)


def is_empty_criteria(analyst_json: dict) -> bool:
    """Check if region, category, preferences are all empty."""
    region = analyst_json.get("region") or []
    category = analyst_json.get("category") or []
    preferences = analyst_json.get("preferences") or []
    return not region and not category and not preferences


def process_chat(country_id: int, user_message: str) -> dict:
    """Two-step LLM pipeline with Redis caching.

    Cache key includes: country, user_message, system_prompt, model params.
    TTL: CACHE_TTL (default 600s = 10 min).
    Returns parsed JSON dict from LLM, or fallback dict on error.
    """
    auth_key = os.getenv("LLM_AUTH_KEY")
    if not auth_key:
        raise RuntimeError("Сервис временно недоступен, попробуйте позже")

    country_name = get_country_name(country_id)
    if not country_name:
        raise ValueError(f"Country {country_id} not found")

    try:
        # ---- Step 1: Analyst ----
        system1 = build_analyst_prompt(country_name, user_message)
        logger.info("step=analyst system_prompt=%s", system1[:200])
        analyst_cache_key = (
            "analyst",
            country_name,
            user_message,
            system1,
            os.getenv("LLM_MODEL", "GigaChat-3-Lightning"),
            str(os.getenv("LLM_TEMPERATURE", 0.7)),
        )

        cached = cache_get(analyst_cache_key)
        if cached and not cached.startswith("К сожалению"):
            analyst_response = cached
        else:
            analyst_response = chat_completion(
                auth_key, country_name, user_message,
                system_prompt_override=system1,
            )
            logger.info("step=analyst response=%s", analyst_response[:500])
            cache_set(analyst_cache_key, analyst_response)
        parsed = _parse_analyst_response(analyst_response)
        empty_criteria = is_empty_criteria(parsed)
        json_str = json.dumps(parsed, ensure_ascii=False, indent=2)

        # ---- Step 2: Travel expert ----
        system2 = build_travel_expert_prompt(json_str)
        logger.info("step=expert system_prompt=%s", system2[:200])
        expert_cache_key = (
            "expert",
            json_str,
            system2,
            os.getenv("LLM_MODEL", "GigaChat-3-Lightning"),
            str(os.getenv("LLM_TEMPERATURE", 0.7)),
        )

        cached = cache_get(expert_cache_key)
        if cached and not cached.startswith("К сожалению"):
            json_str = extract_json(cached)
            if json_str is None:
                raise RuntimeError("Попробуйте повторить запрос")
            result = json.loads(json_str)
            if empty_criteria:
                result["message"] = (
                    "Вы не задали ни одного критерия для подборки отелей. "
                    "Вот на всякий случай несколько отелей по запрошенной вами стране."
                )
            return result

        expert_response = chat_completion(
            auth_key, country_name, user_message,
            system_prompt_override=system2,
        )
        logger.info("step=expert response_full=%s", expert_response)
        cache_set(expert_cache_key, expert_response)
        logger.info("step=expert response=%s", expert_response[:500])

        json_str = extract_json(expert_response)
        if json_str is None:
            raise RuntimeError("Попробуйте повторить запрос")
        result = json.loads(json_str)

        if empty_criteria:
            result["message"] = (
                "Вы не задали ни одного критерия для подборки отелей. "
                "Вот на всякий случай несколько отелей по запрошенной вами стране."
            )

        return result

    except json.JSONDecodeError:
        raise RuntimeError("Попробуйте повторить запрос") from None
    except RuntimeError:
        raise
    except Exception:
        raise RuntimeError("Сервис временно недоступен, попробуйте позже")
