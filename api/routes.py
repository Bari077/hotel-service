"""Routes and endpoint handlers."""

from flask import Blueprint, request, jsonify

from api.schemas import ChatRequest, ChatResponse
from services.service import process_chat

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/chat", methods=["POST"])
def chat():
    """Accept countryId + message, forward to GigaChat, return reply."""
    try:
        data = ChatRequest.model_validate(request.get_json(force=True))
    except Exception as e:
        return jsonify({"error": str(e)}), 422

    try:
        reply = process_chat(data.countryId, data.message)
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"LLM error: {e}"}), 502

    response = ChatResponse(countryId=data.countryId, message=reply, status="ok")
    return jsonify(response.model_dump()), 200
