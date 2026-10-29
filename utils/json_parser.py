"""JSON extraction from LLM responses."""

import json


def extract_json(text: str) -> str | None:
    """Try to parse JSON from LLM response.

    If direct parse fails, try to find the outermost valid JSON object.
    Handles cases like nested JSON inside strings (malformed LLM output).
    """
    # Try direct parse first
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    # Try to find outermost {...} by counting braces
    start = None
    depth = 0
    for i, char in enumerate(text):
        if char == "{":
            if depth == 0:
                start = i
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and start is not None:
                candidate = text[start:i + 1]
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    start = None
                    continue

    return None
