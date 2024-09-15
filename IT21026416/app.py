from flask import Flask, request, jsonify
from flask_cors import CORS
from NLPEngine import classify_text_with_context  # Import the enhanced classify_text function
import openai
import logging
import os

app = Flask(__name__)
CORS(app)  # Enable CORS to allow cross-origin requests from frontend

# Set up logging to a file
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

# Load OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get data from request
        data = request.json

        # If inputText is missing or request is malformed
        if not data or "inputText" not in data:
            return jsonify({"error": "Invalid request: 'inputText' not provided"}), 400

        # Process input_text using the enhanced NLP Engine
        input_text = data.get("inputText")
        logging.info(f"Received input text: {input_text}")  # Log received input
        classification_result = classify_text_with_context(input_text)

        # Prepare the response with classification and justification
        response = {
            "message": f"Analyzed: {input_text}",
            "label": classification_result['label'],
            "justification": classification_result['justification'],
            "suggested_policies": classification_result.get('suggested_policies', [])
        }

        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error in analyze endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/openai', methods=['POST'])
def get_openai_explanation():
    try:
        data = request.json
        input_text = data.get("inputText")

        # Use OpenAI API to get explanation
        explanation = openai.Completion.create(
            engine="davinci",
            prompt=f"Explain why the following security policy is recommended: {input_text}",
            max_tokens=150
        )

        return jsonify({"explanation": explanation.choices[0].text.strip()})

    except Exception as e:
        logging.error(f"Error in OpenAI explanation endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get data from request
        data = request.json

        # Extract classification and specifications from the form data
        classification = data.get('classification', None)
        if not classification or classification not in ['Threat Prevention', 'Data Leakage']:  # Ensure classification matches expected values
            return jsonify({'status': 'failure', 'message': 'Invalid classification specified'}), 400

        # Process policies based on classification and other form data
        specifications = {key: value for key, value in data.items() if key != 'classification'}

        # Pass the specifications to the policy generation logic
        from policy_generator import generate_policy_files
        policy_file_path = generate_policy_files(specifications)

        return jsonify({'status': 'success', 'policy_file_path': policy_file_path})

    except Exception as e:
        return jsonify({'status': 'failure', 'message': f'Error generating policies: {str(e)}'}), 500


if __name__ == '__main__':
    # To run the app locally
    app.run(debug=True)
