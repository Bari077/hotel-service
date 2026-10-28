"""Core service implementations."""

import os

from llm.model import chat_completion


def process_chat(country_id: int, user_message: str) -> str:
    """Process a user chat request by sending it to GigaChat."""
    auth_key = os.getenv("LLM_AUTH_KEY")
    if not auth_key:
        raise ValueError("LLM_AUTH_KEY environment variable is not set")

    return chat_completion(auth_key, country_id, user_message)
