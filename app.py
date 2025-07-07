from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

KLAVIYO_API_KEY = os.environ.get("KLAVIYO_API_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()

        # 🔍 Search for the email in all answers
        email = None
        for answer in data.get("form_response", {}).get("answers", []):
            if answer.get("type") == "email":
                email = answer.get("email")
                break

        if not email:
            return jsonify({"error": "Email not found in webhook payload"}), 400

        # 📤 Prepare request to Klaviyo
        url = f"https://a.klaviyo.com/api/profiles/"
        headers = {
            "Authorization": f"Klaviyo-API-Key {KLAVIYO_API_KEY}",
            "Content-Type": "application/json",
            "revision": "2023-02-22"
        }
        payload = {
            "data": {
                "type": "profile",
                "attributes": {
                    "email": email,
                    "suppressed": False
                }
            }
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return jsonify({"message": "Successfully unsuppressed"}), 200
        else:
            return jsonify({"error": "Failed to unsuppress", "details": response.text}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for Render.com to detect the open port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
