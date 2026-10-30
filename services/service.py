"""Core service implementations."""

import json
import os
import logging

from services.countries import get_country_name
from cache.cache import cache_get, cache_set, cache_delete
from llm.model import chat_completion
from llm.prompts import build_analyst_prompt, build_travel_expert_prompt
from llm.schemas import AnalystResponse, TravelExpertResponse

logger = logging.getLogger("hotel-service")


def is_empty_criteria(analyst_data: AnalystResponse) -> bool:
    """Check if region, category, preferences are all empty."""
    return (
        not analyst_data.region
        and not analyst_data.category
        and not analyst_data.preferences
    )


def process_chat(country_id: int, user_message: str) -> dict:
    """Two-step LLM pipeline with Redis caching and Structured Output.

    Uses Pydantic models for Structured Output — no manual JSON parsing needed.
    Cache key includes: country, user_message, system_prompt, model params.
    TTL: CACHE_TTL (default 600s = 10 min).
    Returns parsed dict from LLM, or fallback dict on error.
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
            os.getenv("LLM_MODEL", "GigaChat-2"),
            str(os.getenv("LLM_TEMPERATURE", 0.7)),
        )

        cached = cache_get(analyst_cache_key)
        if cached and not cached.startswith("К сожалению"):
            # Validate cached JSON
            try:
                json.loads(cached)
                analyst_response = cached
            except json.JSONDecodeError:
                logger.warning("CACHE INVALID analyst, deleting")
                cache_delete(analyst_cache_key)
                cached = None

        if not cached:
            analyst_parsed = chat_completion(
                auth_key, country_id, user_message,
                system_prompt_override=system1,
                response_model=AnalystResponse,
            )
            analyst_response = analyst_parsed.model_dump_json(indent=2)
            logger.info("step=analyst response=%s", analyst_response[:500])
            cache_set(analyst_cache_key, analyst_response)
        else:
            analyst_parsed = AnalystResponse.model_validate_json(cached)

        empty_criteria = is_empty_criteria(analyst_parsed)

        # ---- Step 2: Travel expert ----
        system2 = build_travel_expert_prompt(analyst_parsed.model_dump_json(indent=2, ensure_ascii=False))
        logger.info("step=expert system_prompt=%s", system2[:200])
        expert_cache_key = (
            "expert",
            analyst_parsed.model_dump_json(indent=2, ensure_ascii=False),
            system2,
            os.getenv("LLM_MODEL", "GigaChat-2"),
            str(os.getenv("LLM_TEMPERATURE", 0.7)),
        )

        cached = cache_get(expert_cache_key)
        if cached and not cached.startswith("К сожалению"):
            # Validate cached JSON
            try:
                json.loads(cached)
                result = TravelExpertResponse.model_validate_json(cached)
                if empty_criteria:
                    result.travelRecommendation = (
                        "Вы не задали ни одного критерия для подборки отелей. "
                        "Вот на всякий случай несколько отелей по запрошенной вами стране."
                    )
                return result.model_dump(mode="json", exclude_unset=True)
            except Exception:
                logger.warning("CACHE INVALID expert, deleting")
                cache_delete(expert_cache_key)
                cached = None

        expert_parsed = chat_completion(
            auth_key, country_id, user_message,
            system_prompt_override=system2,
            response_model=TravelExpertResponse,
        )
        expert_response = expert_parsed.model_dump_json(indent=2, ensure_ascii=False)
        cache_set(expert_cache_key, expert_response)
        logger.info("step=expert response=%s", expert_response[:500])

        result_dict = expert_parsed.model_dump(mode="json", exclude_unset=True)

        if empty_criteria:
            result_dict["message"] = (
                "Вы не задали ни одного критерия для подборки отелей. "
                "Вот на всякий случай несколько отелей по запрошенной вами стране."
            )

        return result_dict

    except RuntimeError:
        raise
    except Exception:
        logger.error("process_chat_error countryId=%s", country_id, exc_info=True)
        raise RuntimeError("Сервис временно недоступен, попробуйте позже")
