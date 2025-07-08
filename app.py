from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

KLAVIYO_API_KEY = os.environ.get("KLAVIYO_API_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("Incoming Typeform payload:", data)

        # Extract email from Typeform webhook
        email = None
        for answer in data.get("form_response", {}).get("answers", []):
            if answer.get("type") == "email":
                email = answer.get("email")
                break

        if not email:
            return jsonify({"error": "Email not found in webhook payload"}), 400

        # Call Klaviyo unsuppress API
        url = "https://a.klaviyo.com/api/profile-suppression-bulk-deletion-jobs/"
        headers = {
            "Authorization": f"Klaviyo-API-Key {KLAVIYO_API_KEY}",
            "revision": "2023-10-15",
            "Content-Type": "application/json"
        }
        payload = {
            "data": {
                "type": "profile-suppression-bulk-deletion-job",
                "attributes": {
                    "emails": [email]
                }
            }
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 202:
            return jsonify({"message": "Successfully unsuppressed"}), 202
        else:
            return jsonify({
                "error": "Failed to unsuppress",
                "details": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
