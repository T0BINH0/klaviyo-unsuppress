from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Your webhook endpoint
@app.route('/webhook', methods=['POST', 'PUT'])
def webhook():
    if request.method == 'PUT':
        # Accept and ignore PUT requests to avoid errors
        return jsonify({'message': 'PUT method acknowledged'}), 200

    try:
        data = request.get_json()

        # Optional: Print data for debugging
        print("Received data:", data)

        # Extract email from Typeform response structure
        email = data['form_response']['answers'][0]['email']  # Adjust index if needed

        # Klaviyo API call to unsuppress contact
        headers = {
            "Authorization": f"Klaviyo-API-Key {os.getenv('KLAVIYO_API_KEY')}",
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

        response = requests.put(
            "https://a.klaviyo.com/api/profiles/",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            return jsonify({'message': 'Successfully unsuppressed'}), 200
        else:
            return jsonify({
                'error': 'Failed to unsuppress',
                'details': response.text
            }), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Start the Flask app (Render detects this automatically)
if __name__ == '__main__':
    app.run(debug=True)
