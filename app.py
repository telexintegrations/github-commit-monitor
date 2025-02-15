from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import hmac
import hashlib
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://telex.im", "https://staging.telex.im", "http://telextest.im", "http://staging.telextest.im"]}})

# Telex API Configuration
TELEX_API_URL = "https://ping.telex.im/v1/webhooks/{channel_id}"
GITHUB_SECRET = os.getenv("GITHUB_SECRET")
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
        # Verify GitHub signature
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not verify_signature(request.data, signature):
            return jsonify({"error": "Unauthorized"}), 401

        # Parse GitHub payload
        payload = request.json
        commit_message = payload["head_commit"]["message"]
        author = payload["head_commit"]["author"]["name"]
        repo_name = payload["repository"]["name"]

        # Format message for Telex
        telex_message = f"🚀 New commit in *{repo_name}* by **{author}**: `{commit_message}`"

        # Send to Telex
        response = requests.post(
            TELEX_API_URL.format(channel_id=CHANNEL_ID),
            json={"text": telex_message}
        )

        if response.status_code != 200:
            return jsonify({"error": "Failed to send message to Telex"}), response.status_code

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Integration JSON endpoint
@app.route("/integration.json", methods=["GET"])
def get_integration_json():
    base_url = request.url_root.rstrip("/")
    integration_json = {
        "data": {
            "date": {"created_at": "2025-02-15", "updated_at": "2025-02-15"},
            "descriptions": {
                "app_name": "GitHub Commit Tracker",
                "app_description": "Tracks commits and sends notifications to Telex.",
                "app_logo": "https://i.imgur.com/bRoRB1Y.png",
                "app_url": base_url,
                "background_color": "#fff",
            },
            "is_active": True,
            "integration_type": "modifier",
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

if __name__ == "__main__":
    app.run(port=5000, debug=True)