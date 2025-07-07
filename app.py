from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

KLAVIYO_API_KEY = os.environ.get("KLAVIYO_API_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()

        # 🔍 Extract email from Typeform webhook
        email = None
        for answer in data.get("form_response", {}).get("answers", []):
            if answer.get("type") == "email":
                email = answer.get("email")
                break

        if not email:
            return jsonify({"error": "Email not found in webhook payload"}), 400

        # ✅ Correct legacy endpoint
        url = "https://a.klaviyo.com/api/v1/people/exclusions/email"
        params = {
            "api_key": KLAVIYO_API_KEY,
            "email": email
        }

        response = requests.delete(url, params=params)

        if response.status_code == 200:
            return jsonify({"message": "Successfully unsuppressed"}), 200
        else:
            return jsonify({
                "error": "Failed to unsuppress",
                "details": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
