from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

KLAVIYO_API_KEY = os.getenv("pk_b6f0b4c176168e0a56d5356ee9b872373f")

def is_suppressed(email):
    url = f"https://a.klaviyo.com/api/profiles/?filter=equals(email,'{email}')"
    headers = {
        "Authorization": f"Bearer {KLAVIYO_API_KEY}",
        "accept": "application/json",
        "revision": "2023-02-22"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        try:
            profile_id = data['data'][0]['id']
            is_suppressed = data['data'][0]['attributes']['suppressed']['email']
            return profile_id, is_suppressed
        except:
            return None, False
    return None, False

def unsuppress_profile(profile_id):
    url = f"https://a.klaviyo.com/api/profile-suppressions/{profile_id}/email-suppression"
    headers = {
        "Authorization": f"Bearer {KLAVIYO_API_KEY}",
        "accept": "application/json",
        "revision": "2023-02-22"
    }
    response = requests.delete(url, headers=headers)
    return response.status_code == 204

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Missing email"}), 400

    profile_id, suppressed = is_suppressed(email)

    if suppressed and profile_id:
        if unsuppress_profile(profile_id):
            return jsonify({"message": f"{email} was unsuppressed"}), 200
        else:
            return jsonify({"error": "Failed to unsuppress"}), 500
    else:
        return jsonify({"message": f"{email} was not suppressed or already active"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Webhook is running!", 200
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
