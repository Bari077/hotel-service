"""Entry point for hotel-service."""

import os
from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["DEBUG"] = os.getenv("DEBUG", "true").lower() == "true"

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
