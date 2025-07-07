from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

KLAVIYO_API_KEY = os.environ.get("KLAVIYO_API_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()

        # 🔍 Extract the email from Typeform payload
        email = data.get("form_response", {}).get("answers", [])[0].get("email")

        if not email:
            return jsonify({"error": "Email not found in webhook payload"}), 400

        # 🛠️ Prepare request to Klaviyo
        url = "https://a.klaviyo.com/api/profiles/"
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
                    "suppression": {
                        "email": False
                    }
                }
            }
        }

        # ✅ Send PATCH request to unsuppress
        response = requests.patch(url, json=payload, headers=headers)

        if response.status_code >= 200 and response.status_code < 300:
            return jsonify({"status": "unsuppressed", "email": email}), 200
        else:
            return jsonify({
                "error": "Failed to unsuppress",
                "details": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 📢 Required by Render to expose the correct port
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
