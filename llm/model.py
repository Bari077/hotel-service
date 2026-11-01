"""LLM model client and inference logic."""

import os
import time
import uuid
import urllib3
import logging
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

logger = logging.getLogger("hotel-service")

# Load .env variables
load_dotenv()

# Suppress SSL warnings for self-signed Sberbank certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_TOKEN_CACHE: dict[str, dict] = {}
_VERIFY_SSL = os.getenv("LLM_VERIFY_SSL", "false").lower() == "true"
_REQUEST_TIMEOUT = int(os.getenv("LLM_REQUEST_TIMEOUT", 30))
_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", 3))


def get_access_token(authorization_key: str) -> str:
    """Obtain a GigaChat access token using the authorization key.

    The token is cached for 30 minutes to avoid redundant calls.
    """
    now = time.time()
    if authorization_key in _TOKEN_CACHE:
        cached = _TOKEN_CACHE[authorization_key]
        if now < cached["expires_at"]:
            return cached["token"]

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {authorization_key}",
    }
    payload = {"scope": "GIGACHAT_API_PERS"}

    response = requests.post(url, headers=headers, data=payload, verify=_VERIFY_SSL)
    response.raise_for_status()

    data = response.json()
    token = data["access_token"]
    expires_in = data.get("expires_in", 1800)

    _TOKEN_CACHE[authorization_key] = {
        "token": token,
        "expires_at": now + expires_in,
    }

    return token


def _make_request(
    token: str,
    system_prompt: str,
    user_prompt: str,
    response_model: type[BaseModel] | None = None,
) -> str | BaseModel:
    """Make a single HTTP request to GigaChat API.

    If response_model is provided, uses Structured Output with json_schema.
    Otherwise returns raw text content.
    """
    url = "https://api.giga.chat/v1/chat/completions"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": os.getenv("LLM_MODEL", "GigaChat-2-Pro"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": int(os.getenv("LLM_MAX_TOKENS", 1024)),
        "temperature": float(os.getenv("LLM_TEMPERATURE", 0.7)),
    }

    # Add Structured Output if model is provided
    if response_model is not None:
        payload["response_format"] = {
            "type": "json_schema",
            "schema": response_model.model_json_schema(),
            "strict": True,
        }
        logger.info(
            "llm_request system_prompt_len=%d user_prompt_len=%d model=%s structured=%s",
            len(system_prompt),
            len(user_prompt),
            os.getenv("LLM_MODEL", "GigaChat-2-Pro"),
            response_model.__name__,
        )
    else:
        logger.info(
            "llm_request system_prompt_len=%d user_prompt_len=%d model=%s",
            len(system_prompt),
            len(user_prompt),
            os.getenv("LLM_MODEL", "GigaChat-2-Pro"),
        )

    start = time.time()
    response = requests.post(
        url, headers=headers, json=payload,
        timeout=_REQUEST_TIMEOUT, verify=_VERIFY_SSL,
    )
    duration_ms = round((time.time() - start) * 1000)
    response.raise_for_status()

    data = response.json()
    logger.info("llm_response duration_ms=%d", duration_ms)

    content = data["choices"][0]["message"]["content"]

    # If response_model is provided, parse the JSON string into the model
    if response_model is not None:
        try:
            parsed = response_model.model_validate_json(content)
            return parsed
        except Exception as e:
            logger.error(
                "structured_parse_failed model=%s error=%s content=%s",
                response_model.__name__,
                e,
                content[:200],
            )
            raise

    return content


def chat_completion(
    authorization_key: str,
    country_id: int,
    user_message: str,
    system_prompt_override: str | None = None,
    user_prompt_override: str | None = None,
    response_model: type[BaseModel] | None = None,
) -> str | BaseModel:
    """Send a prompt to GigaChat with retry and timeout.

    - Timeout: configurable via LLM_REQUEST_TIMEOUT (default 30s)
    - Retry: up to LLM_MAX_RETRIES (default 3) with exponential backoff
    - response_model: optional Pydantic model for Structured Output
    - Raises LLMTimeoutError on timeout
    - Raises LLMUnavailableError on auth/5xx failures
    - Raises RuntimeError on other failures
    """
    try:
        token = get_access_token(authorization_key)
    except requests.exceptions.RequestException:
        logger.error("auth_failed authorization_key=%s", authorization_key[:20])
        from services.service import LLMUnavailableError
        raise LLMUnavailableError("Сервис временно недоступен, попробуйте позже")

    if system_prompt_override:
        system_prompt = system_prompt_override
        user_prompt = user_prompt_override or ""
    else:
        from services.service import LLMUnavailableError
        raise LLMUnavailableError("Сервис временно недоступен, попробуйте позже")

    logger.info(
        "llm_prompt system=%s user=%s model=%s",
        system_prompt[:200],
        user_prompt[:200],
        response_model.__name__ if response_model else "text",
    )

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            return _make_request(
                token, system_prompt, user_prompt, response_model
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            logger.warning("llm_timeout attempt=%d/%d", attempt, _MAX_RETRIES)
            if attempt == _MAX_RETRIES:
                from services.service import LLMTimeoutError
                raise LLMTimeoutError("Модель LLM пока недоступна, попробуйте позже")
            wait = 2 ** (attempt - 1)
            time.sleep(wait)
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            if status >= 500:
                logger.warning(
                    "llm_5xx status=%d attempt=%d/%d",
                    status,
                    attempt,
                    _MAX_RETRIES,
                )
                if attempt == _MAX_RETRIES:
                    from services.service import LLMUnavailableError
                    raise LLMUnavailableError("Модель LLM пока недоступна, попробуйте позже")
                wait = 2 ** (attempt - 1)
                time.sleep(wait)
            else:
                logger.error("llm_4xx status=%d", status)
                from services.service import LLMUnavailableError
                raise LLMUnavailableError("Модель LLM пока недоступна, попробуйте позже")

    from services.service import LLMUnavailableError
    raise LLMUnavailableError("Модель LLM пока недоступна, попробуйте позже")
