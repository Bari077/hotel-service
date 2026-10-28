"""LLM model client and inference logic."""

import os
import time
import uuid
import urllib3
import requests
from dotenv import load_dotenv

from llm.prompts import build_prompt

# Load .env variables
load_dotenv()

# Suppress SSL warnings for self-signed Sberbank certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_TOKEN_CACHE: dict[str, dict] = {}
_VERIFY_SSL = os.getenv("LLM_VERIFY_SSL", "false").lower() == "true"


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


def chat_completion(authorization_key: str, country_id: int, user_message: str) -> str:
    """Send a prompt to GigaChat and return the assistant's reply."""
    token = get_access_token(authorization_key)

    system_prompt, user_prompt = build_prompt(country_id, user_message)

    url = "https://api.giga.chat/v1/chat/completions"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": os.getenv("LLM_MODEL", "GigaChat-3-Lightning"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": int(os.getenv("LLM_MAX_TOKENS", 1024)),
        "temperature": float(os.getenv("LLM_TEMPERATURE", 0.7)),
    }

    response = requests.post(url, headers=headers, json=payload, verify=_VERIFY_SSL)
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]
