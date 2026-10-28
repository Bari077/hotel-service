"""Entry point for hotel-service."""

import os
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DEBUG"] = os.getenv("DEBUG", "true").lower() == "true"

    from api.routes import api_bp
    app.register_blueprint(api_bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    print(f"Starting {os.getenv('APP_NAME', 'hotel-service')} on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
