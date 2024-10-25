from flask import Flask, request, jsonify
from NLPEngine import classify_text_with_context  # Import the enhanced classify_text function
from flask_cors import CORS
import openai
import logging
import os
import json

# Initialize logging
logging.basicConfig(level=logging.DEBUG,  # Set log level to DEBUG to capture all logs
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)
CORS(app)  # Enable CORS to allow cross-origin requests from frontend

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
            "message": f"{input_text}",
            "label": classification_result['label'],
            "justification": classification_result['justification'],
            "suggested_policies": classification_result.get('suggested_policies', [])
        }

        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error in analyze endpoint: {str(e)}")  # Log the full error
        return jsonify({"error": str(e)}), 500

@app.route('/openai', methods=['POST'])
def get_openai_explanation():
    try:
        data = request.json
        input_text = data.get("inputText")
        explanation = ""
        max_tokens = 250  # Increased tokens for longer responses
        prompt = f"You are a cybersecurity expert. Explain why the following policy is classified under Threat Prevention: {input_text}"
        max_retries = 5  # Limit retries to prevent infinite loops
        retry_count = 0
        
        # Loop to handle continuation if response is incomplete
        while True:
            response = openai.Completion.create(
                engine="gpt-4",  # Using GPT-4 model as seen in the logs
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.7,  # Adjusted for detailed responses
                n=1,
                stop=None
            )

            # Extract and append the response text
            response_text = response.choices[0].text.strip()
            explanation += response_text

            # Check if the response ends with a complete thought
            if response_text.endswith('.') or response_text.endswith('!') or response_text.endswith('?'):
                break
            elif retry_count >= max_retries:
                # Final prompt to request a conclusion if retry limit is reached
                explanation += " [Note: Explanation may be incomplete. Please conclude.]"
                break
            else:
                # Adjust the continuation prompt to guide the model better
                prompt = f"Please continue and complete the explanation: {response_text}"
                retry_count += 1

        return jsonify({"explanation": explanation})

    except Exception as e:
        logging.error(f"Error in OpenAI explanation endpoint: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/logs', methods=['GET'])
def get_logs():
    logs_folder = 'D:/NLP/NLPFinal/Main/logs'  # Folder containing your log files
    logs = []

    # Ensure the logs folder exists before proceeding
    if not os.path.exists(logs_folder):
        return jsonify({"error": f"Logs folder not found: {logs_folder}"}), 404

    # List all JSON files in the logs folder
    for log_file in os.listdir(logs_folder):
        if log_file.endswith('.json'):
            logs.append(log_file)  # Append just the file name, not the content

    return jsonify(logs)

@app.route('/logs/<filename>', methods=['GET'])
def get_log_file(filename):
    logs_folder = 'D:/NLP/NLPFinal/Main/logs'  # Path to the logs folder
    file_path = os.path.join(logs_folder, filename)

    # Debugging: Print the file path being requested
    logging.debug(f"Requested log file path: {file_path}")

    # Check if the file exists
    if not os.path.exists(file_path):
        logging.error(f"Log file not found: {filename}")
        return jsonify({"error": f"Log file not found: {filename}"}), 404

    # Return the log file content
    try:
        with open(file_path, 'r') as file:
            log_content = json.load(file)
        return jsonify(log_content)
    except Exception as e:
        logging.error(f"Error reading log file {filename}: {str(e)}")
        return jsonify({"error": f"Error reading log file {filename}: {str(e)}"}), 500


@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get data from request
        data = request.json

        # Extract classification and specifications from the form data
        classification = data.get('classification', None)
        if not classification or classification not in ['Threat Prevention', 'Data Leakage']:
            return jsonify({'status': 'failure', 'message': 'Invalid classification specified'}), 400

        # Process policies based on classification and other form data
        specifications = {key: value for key, value in data.items() if key != 'classification'}

        # Pass the specifications to the policy generation logic
        from policy_generator import generate_policy_files
        policy_file_path = generate_policy_files(specifications)

        return jsonify({'status': 'success', 'policy_file_path': policy_file_path})

    except Exception as e:
        return jsonify({'status': 'failure', 'message': f'Error generating policies: {str(e)}'}), 500

@app.route('/dashboard', methods=['GET'])
def dashboard():
    logs_folder = 'logs'
    policy_count = 0
    recent_policies = []
    threat_prevention_count = 0
    data_leakage_count = 0
    other_count = 0

    # Traverse the logs folder and gather data
    for filename in os.listdir(logs_folder):
        if filename.endswith('.json'):
            policy_count += 1
            with open(os.path.join(logs_folder, filename), 'r') as policy_file:
                try:
                    policy_data = json.load(policy_file)

                    # Check the type of policy and update counts
                    policy_type = policy_data.get('policyType', 'Other')
                    if policy_type == 'Threat Prevention':
                        threat_prevention_count += 1
                    elif policy_type == 'Data Leakage':
                        data_leakage_count += 1
                    else:
                        other_count += 1

                    # Add the latest policies to recent policies list
                    if len(recent_policies) < 5:
                        recent_policies.append({
                            'policyType': policy_type,
                            'details': policy_data.get('details', 'N/A'),
                            'timestamp': policy_data.get('timestamp', 'N/A')
                        })

                except json.JSONDecodeError:
                    logging.error(f"Error reading or parsing file: {filename}")
    
    # Prepare data for the dashboard
    dashboard_data = {
        'policyCount': policy_count,
        'recentPolicies': recent_policies,
        'threatPreventionCount': threat_prevention_count,
        'dataLeakageCount': data_leakage_count,
        'otherCount': other_count,
        # Example data, adjust as needed
        'blockingDownloadsCount': 5,
        'safeBrowsingCount': 10,
        'cookiesBlockedCount': 8,
        'blockingSitesCount': 4
    }

    return jsonify(dashboard_data)

if __name__ == '__main__':
    # To run the app locally with debug logging
    app.run(debug=True, use_reloader=True)
