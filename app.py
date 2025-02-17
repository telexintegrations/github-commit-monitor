from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import hmac
import hashlib
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
allowed_origins = [
    "https://telex.im",
    "https://staging.telex.im",
    "http://telextest.im",
    "http://staging.telextest.im"
]

CORS(app, resources={
    r"/*": {
        "origins": allowed_origins,
        "supports_credentials": True
    }
})

# Telex API Configuration
TELEX_API_URL = "https://ping.telex.im/v1/webhooks/{channel_id}"
GITHUB_SECRET = os.getenv("MY_GITHUB_SECRET")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Verify GitHub Webhook Signature
def verify_signature(payload, signature):
    secret = GITHUB_SECRET.encode()
    digest = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={digest}", signature)

# Handle GitHub Webhook
@app.route("/github-webhook", methods=["POST"])
def github_webhook():
    try:
        logger.info("Received webhook payload")
        logger.info(f"Headers: {request.headers}")
        logger.info(f"Payload: {request.json}")

        # # Verify GitHub signature
        # signature = request.headers.get("X-Hub-Signature-256", "")
        # if not verify_signature(request.data, signature):
        #     return jsonify({"error": "Unauthorized"}), 401

        # Verify GitHub signature
        # GitHub sends webhook with signature
        signature = request.headers.get("X-Hub-Signature-256", "")
        logger.info(f"Received signature: {signature}")

        # 2. Server verifies if signature is from GitHub
        if not verify_signature(request.data, signature):
            logger.error("Signature verification failed")
            return jsonify({"error": "Unauthorized"}), 401

        # Parse GitHub payload
        payload = request.json
        commit_message = payload["head_commit"]["message"]
        author = payload["head_commit"]["author"]["name"]
        repo_name = payload["repository"]["name"]

        # Format message for Telex
        telex_payload = {
            "event_name": "GitHub Commit",
            "message": f" 🎉 New commit in {repo_name} by {author}: {commit_message}",
            "status": "success",
            "username": author
        }

        # Send to Telex with logging
        logger.info(f"Sending to Telex: {telex_payload}")
        response = requests.post(
            TELEX_API_URL.format(channel_id=CHANNEL_ID),
            json=telex_payload,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            }
        )

        logger.info(f"Telex response: {response.status_code} - {response.text}")

        if response.status_code != 202:  # Telex returns 202 for success
            return jsonify({"error": "Failed to send message to Telex"}), response.status_code

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Integration JSON endpoint
@app.route("/integration.json", methods=["GET"])
def get_integration_json():
    base_url = request.url_root.rstrip('/')
    integration_json = {
        "data": {
                "created_at": "2025-02-17",  
        "updated_at": "2025-02-17",
        "description": {
                "app_name": "GitHub Commit Tracker",
                "app_description": "Tracks commits and sends notifications to Telex.",
                "app_logo": "",
                "app_url": base_url,
                "background_color": "#ffffff",
            },
            "is_active": True,
            "integration_type": "output",
            "key_features": [
                "Tracks GitHub commits and sends notifications to Telex",
                "Provides real-time updates",
                "Easy integration with GitHub",
                "Customizable notifications"
            ],
            "integration_category": "Development & Code Management",
            "author": "Cynthia Wahome",
            "website": base_url,
            "settings": [
                {"label": "webhook-slug", "type": "text", "required": True, "default": ""},
            ],
            "target_url": f"{base_url}/github-webhook",
        }
    }
    return jsonify(integration_json)

# Health Check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Root URL endpoint
@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Welcome to the GitHub Commit Tracker API"}), 200

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "error": "Method not allowed. This endpoint only accepts POST requests.",
        "allowed_methods": ["POST"]
    }), 405

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  