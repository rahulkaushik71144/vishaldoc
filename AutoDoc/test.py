from flask import Flask, request, jsonify
from gradio_client import Client

# Initialize Flask app
app = Flask(__name__)

# Initialize the Gradio client for CodeGeeX
client = Client("THUDM/CodeGeeX")

@app.route('/generate_code')
def generate_code():
    message = request.args.get('message')

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Call the Gradio model's prediction API
        result = client.predict(
            message=message,
            api_name="/chat"
        )

        # Return the generated result
        return jsonify({"generated_code": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main entry point
if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
