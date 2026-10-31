"""Entry point for hotel-service."""

import os
from flask import Flask, jsonify
from dotenv import load_dotenv

from utils.logging import setup_logger

load_dotenv()
logger = setup_logger()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DEBUG"] = os.getenv("DEBUG", "false").lower() == "true"

    from api.routes import api_bp
    app.register_blueprint(api_bp)

    from api.views import web_bp
    app.register_blueprint(web_bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print(f"Starting {os.getenv('APP_NAME', 'hotel-service')} on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
