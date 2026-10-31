"""Core service implementations."""

import json
import os
import logging

from pydantic import ValidationError

from cache.cache import cache_get, cache_set, cache_delete
from llm.model import chat_completion
from llm.prompts import build_analyst_prompt, build_travel_expert_prompt
from llm.schemas import AnalystResponse, TravelExpertResponse

logger = logging.getLogger("hotel-service")


# Custom exceptions for user-friendly error messages
class LLMUnavailableError(RuntimeError):
    """LLM service is unavailable."""
    pass


class LLMValidationError(RuntimeError):
    """LLM returned invalid response."""
    pass


class LLMTimeoutError(RuntimeError):
    """LLM request timed out."""
    pass


def is_empty_criteria(analyst_data: AnalystResponse) -> bool:
    """Check if region, category, preferences are all empty."""
    return (
        not analyst_data.region
        and not analyst_data.category
        and not analyst_data.preferences
    )


def process_chat(user_message: str) -> dict:
    """Two-step LLM pipeline with Redis caching and Structured Output.

    Uses Pydantic models for Structured Output — no manual JSON parsing needed.
    Cache key includes: country, user_message, system_prompt, model params.
    TTL: CACHE_TTL (default 600s = 10 min).
    Returns parsed dict from LLM, or fallback dict on error.
    """
    auth_key = os.getenv("LLM_AUTH_KEY")
    if not auth_key:
        raise LLMUnavailableError("Сервис временно недоступен, попробуйте позже")

    try:
        # ---- Step 1: Analyst ----
        system1 = build_analyst_prompt(user_message)
        logger.info("step=analyst system_prompt=%s", system1)
        analyst_cache_key = (
            "analyst",
            user_message,
            system1,
            os.getenv("LLM_MODEL", "GigaChat-2-Pro"),
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
            analyst_parsed = None
            max_retries = 2

            for attempt in range(max_retries):
                if attempt > 0:
                    logger.warning("RETRY analyst attempt=%d/%d", attempt + 1, max_retries)
                try:
                    analyst_parsed = chat_completion(
                        auth_key, 0, user_message,
                        system_prompt_override=system1,
                        response_model=AnalystResponse,
                    )
                    analyst_response = analyst_parsed.model_dump_json(indent=2)
                    logger.info("step=analyst response=%s", analyst_response)
                    cache_set(analyst_cache_key, analyst_response)
                    break  # Success — exit retry loop
                except ValidationError as e:
                    logger.error("analyst_validation_error attempt=%d error=%s", attempt + 1, e)
                    if attempt == max_retries - 1:
                        raise LLMValidationError(
                            "Модель вернула некорректный ответ. Попробуйте переформулировать запрос"
                        )
                except LLMTimeoutError:
                    raise
                except LLMUnavailableError:
                    raise
                except Exception:
                    logger.error("analyst_error attempt=%d", attempt + 1, exc_info=True)
                    if attempt == max_retries - 1:
                        raise LLMUnavailableError(
                            "Модель LLM пока недоступна, попробуйте позже"
                        )
        else:
            try:
                analyst_parsed = AnalystResponse.model_validate_json(cached)
            except ValidationError:
                logger.warning("CACHE INVALID analyst, deleting")
                cache_delete(analyst_cache_key)
                raise LLMValidationError(
                    "Модель вернула некорректный ответ. Попробуйте переформулировать запрос"
                )

        country_name = analyst_parsed.country
        empty_criteria = is_empty_criteria(analyst_parsed)

        # ---- Step 2: Travel expert ----
        analyst_json = analyst_parsed.model_dump_json(indent=2, ensure_ascii=False)
        system2 = build_travel_expert_prompt(country_name, analyst_json)
        logger.info("step=expert system_prompt=%s", system2)
        expert_cache_key = (
            "expert",
            analyst_json,
            system2,
            os.getenv("LLM_MODEL", "GigaChat-2-Pro"),
            str(os.getenv("LLM_TEMPERATURE", 0.7)),
        )

        cached = cache_get(expert_cache_key)
        if cached and not cached.startswith("К сожалению"):
            # Validate cached JSON
            try:
                json.loads(cached)
                result = TravelExpertResponse.model_validate_json(cached)
                result_dict = result.model_dump(mode="json", exclude_unset=True)
                if empty_criteria:
                    result_dict["message"] = (
                        "Вы не задали ни одного критерия для подборки отелей. "
                        "Вот на всякий случай несколько отелей по запрошенной вами стране."
                    )
                return result_dict
            except ValidationError:
                logger.warning("CACHE INVALID expert, deleting")
                cache_delete(expert_cache_key)
                cached = None
            except Exception:
                logger.warning("CACHE INVALID expert, deleting")
                cache_delete(expert_cache_key)
                cached = None

        # ---- Expert step with retry on validation failure ----
        expert_parsed = None
        max_retries = 2

        for attempt in range(max_retries):
            if attempt > 0:
                logger.warning("RETRY expert attempt=%d/%d", attempt + 1, max_retries)
            try:
                expert_parsed = chat_completion(
                    auth_key, 0, user_message,
                    system_prompt_override=system2,
                    response_model=TravelExpertResponse,
                )
                expert_response = expert_parsed.model_dump_json(indent=2, ensure_ascii=False)
                cache_set(expert_cache_key, expert_response)
                logger.info("step=expert response=%s", expert_response)
                break  # Success — exit retry loop
            except ValidationError as e:
                logger.error("expert_validation_error attempt=%d error=%s", attempt + 1, e)
                if attempt == max_retries - 1:
                    raise LLMValidationError(
                        "Модель вернула некорректный ответ. Попробуйте переформулировать запрос"
                    )
            except LLMTimeoutError:
                raise
            except LLMUnavailableError:
                raise
            except Exception:
                logger.error("expert_error attempt=%d", attempt + 1, exc_info=True)
                if attempt == max_retries - 1:
                    raise LLMUnavailableError(
                        "Модель LLM пока недоступна, попробуйте позже"
                    )

        result_dict = expert_parsed.model_dump(mode="json", exclude_unset=True)

        if empty_criteria:
            result_dict["message"] = (
                "Вы не задали ни одного критерия для подборки отелей. "
                "Вот на всякий случай несколько отелей по запрошенной вами стране."
            )

        return result_dict

    except (LLMValidationError, LLMTimeoutError, LLMUnavailableError):
        raise
    except Exception:
        logger.error("process_chat_error", exc_info=True)
        raise LLMUnavailableError("Сервис временно недоступен, попробуйте позже")
