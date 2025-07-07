@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("DEBUG: Incoming webhook payload:")
    print(data)  # <--- this will help us see the actual incoming data

    try:
        answers = data.get("form_response", {}).get("answers", [])
        email = None

        for answer in answers:
            if answer.get("type") == "email":
                email = answer.get("email")
                break

        if not email:
            return jsonify({"error": "Missing email"}), 400

        # Call Klaviyo API to unsuppress
        headers = {
            "Authorization": f"Klaviyo-API-Key {os.environ.get('KLAVIYO_API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "profiles": [{"email": email}]
        }

        response = requests.post(
            "https://a.klaviyo.com/api/profiles/unsuppress",
            headers=headers,
            json=payload
        )

        if response.status_code == 202:
            return jsonify({"message": f"{email} was unsuppressed"}), 200
        else:
            return jsonify({"error": "Failed to unsuppress", "details": response.text}), 500

    except Exception as e:
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500
