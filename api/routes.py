"""Routes and endpoint handlers."""

import time

from flask import Blueprint, request, jsonify

from api.schemas import ChatRequest
from services.service import process_chat, LLMUnavailableError, LLMValidationError, LLMTimeoutError

import logging
logger = logging.getLogger("hotel-service")

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/chat", methods=["POST"])
def chat():
    """Accept user message, forward to GigaChat, return parsed JSON."""
    start = time.time()
    ip = request.remote_addr

    try:
        data = ChatRequest.model_validate(request.get_json(force=True))
    except Exception as e:
        errors = e.errors()
        if errors:
            field = errors[0]["loc"][-1]
            msg = errors[0]["msg"]
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, "):]
            logger.warning("validation_error ip=%s field=%s error=%s", ip, field, msg)
            return jsonify({"error": msg}), 422
        logger.warning("validation_error ip=%s error=%s", ip, str(e))
        return jsonify({"error": str(e)}), 422

    try:
        result = process_chat(data.message)
        status = 200
    except LLMTimeoutError as e:
        result = {"error": str(e)}
        status = 503
    except LLMValidationError as e:
        result = {"error": str(e)}
        status = 500
    except LLMUnavailableError as e:
        result = {"error": str(e)}
        status = 503
    except RuntimeError as e:
        result = {"error": str(e)}
        status = 503
    except Exception:
        result = {"error": "Сервис временно недоступен, попробуйте позже"}
        status = 503

    duration_ms = round((time.time() - start) * 1000)
    logger.info(
        "request_complete ip=%s status=%d duration_ms=%d",
        ip, status, duration_ms,
    )
    return jsonify({"message": result, "status": "ok"}), status
