from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    email = data.get('form_response', {}).get('answers', [])[0].get('email', None)

    if not email:
        return jsonify({"error": "Email not found in payload"}), 400

    klaviyo_api_key = os.getenv("KLAVIYO_API_KEY")

    headers = {
        "Authorization": f"Klaviyo-API-Key {klaviyo_api_key}",
        "Content-Type": "application/json",
        "revision": "2023-10-15"
    }

    payload = {
        "data": {
            "type": "profile",
            "attributes": {
                "email": email
            }
        }
    }

    url = "https://a.klaviyo.com/api/profiles/unsuppress-email/"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return jsonify({"message": "Successfully unsuppressed"}), 200
    else:
        return jsonify({
            "error": "Failed to unsuppress",
            "details": response.text
        }), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
