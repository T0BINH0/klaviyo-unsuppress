from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

KLAVIYO_API_KEY = os.environ.get("KLAVIYO_API_KEY")

def mask_email(email):
    try:
        username, domain = email.split("@")
        return username[:2] + "***@" + domain
    except Exception:
        return "***masked***"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        # Extract useful context for logging
        event_id = data.get("event_id", "N/A")
        form_id = data.get("form_response", {}).get("form_id", "N/A")

        print(f"Received webhook: event_id={event_id}, form_id={form_id}")

        # Extract email from answers
        email = None
        for answer in data.get("form_response", {}).get("answers", []):
            if answer.get("type") == "email":
                email = answer.get("email")
                break

        if not email:
            print(f"No email found in payload. event_id={event_id}, form_id={form_id}")
            return jsonify({"error": "Email not found in webhook payload"}), 400

        print(f"Extracted email (masked): {mask_email(email)} | event_id={event_id}, form_id={form_id}")

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
        print(f"Klaviyo response: {response.status_code} | event_id={event_id}, form_id={form_id} | {response.text[:80]}...")

        if response.status_code == 202:
            return jsonify({"message": "Successfully unsuppressed"}), 202
        else:
            return jsonify({
                "error": "Failed to unsuppress",
                "details": response.text[:150]  # Snippet, no PII
            }), response.status_code

    except Exception as e:
        # Try to mask the email if available, but never log raw PII
        email = locals().get('email', None)
        print(f"Webhook error: {str(e)} | event_id={locals().get('event_id', 'N/A')} | form_id={locals().get('form_id', 'N/A')} | email={mask_email(email) if email else 'N/A'}")
        return jsonify({"error": "Server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
