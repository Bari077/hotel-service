"""Routes and endpoint handlers."""

from flask import Blueprint, request, jsonify

from api.schemas import ChatRequest, ChatResponse
from services.service import process_chat

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/chat", methods=["POST"])
def chat():
    """Accept countryId + message, forward to GigaChat, return parsed JSON."""
    try:
        data = ChatRequest.model_validate(request.get_json(force=True))
    except Exception as e:
        errors = e.errors()
        if errors:
            field = errors[0]["loc"][-1]
            msg = errors[0]["msg"]
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, "):]
            return jsonify({"error": msg}), 422
        return jsonify({"error": str(e)}), 422

    try:
        result = process_chat(data.countryId, data.message)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    except Exception:
        return jsonify({"error": "Сервис временно недоступен, попробуйте позже"}), 503

    response = ChatResponse(countryId=data.countryId, message=result, status="ok")
    return jsonify(response.model_dump()), 200
