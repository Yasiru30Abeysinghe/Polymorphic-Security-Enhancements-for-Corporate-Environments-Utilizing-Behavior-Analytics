from flask import Flask, request, render_template, jsonify, redirect, url_for
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import os
import json
import logging

# Load the trained model and tokenizer
model_path = './nlp_model'
model = BertForSequenceClassification.from_pretrained(model_path)
tokenizer = BertTokenizer.from_pretrained(model_path)

# Initialize Flask app
app = Flask(__name__)

# Define categories
categories = [
    'Threat Prevention Policy',
    'Data Leakage Policy',
    'Web Filter Policy'
]

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to classify text
def classify_text(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_id = torch.argmax(logits).item()
    return predicted_class_id

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    text = request.form['security_requirement']
    logging.info(f"Received security requirement: {text}")

    # Check if the input text is empty
    if not text.strip():
        logging.error("Empty security requirement received.")
        return jsonify({'status': 'failure', 'message': 'Empty security requirement'}), 400
    
    # Classify the text
    classification = classify_text(text)
    logging.debug(f"Classifying text: {text}")
    
    
    # Ensure correct category is being passed
    if classification < 0 or classification >= len(categories):
        logging.error("Invalid classification specified.")
        return jsonify({'status': 'failure', 'message': 'Invalid classification specified'}), 400
    
    category = categories[classification]
    logging.info(f"Classification result: {classification} corresponding to category: {category}")
    
    return render_template('policy_form.html', classification=classification, category=category)

# Route for generating and applying policies

@app.route('/generate', methods=['POST'])
def generate():
    try:
        classification = int(request.form.get('classification', -1))
        logging.debug(f"Received classification value: {classification}")
        if classification == -1 or classification >= len(categories):
            logging.error("Invalid classification specified.")
            return jsonify({'status': 'failure', 'message': 'Invalid classification specified'}), 400

        # Capture the "Block all downloads" policy and its conditions
        block_downloads = request.form.get('BlockDownloads', 'no')
        condition = request.form.get('Conditions', 'None')
        condition_value = request.form.get('Values', '')

        specifications = {key: request.form.get(key, 'not_configured') for key in request.form.keys() if key not in ['classification', 'BlockDownloads', 'Conditions', 'Values']}
        
        # Add the BlockDownloads and associated conditions to specifications
        if block_downloads == 'yes':
            specifications['BlockDownloads'] = {
                'enabled': True,
                'condition': condition,
                'value': condition_value
            }
        else:
            specifications['BlockDownloads'] = {
                'enabled': False
            }

        logging.info(f"Specifications to be processed: {specifications}")

        from policy_generator import generate_policy_files
        policy_file_path = generate_policy_files(specifications)
        
        return jsonify({'status': 'success', 'policy_file_path': policy_file_path})

    except Exception as e:
        logging.error(f"Error generating policies: {e}")
        return jsonify({'status': 'failure', 'message': f'Error generating policies: {str(e)}'}), 500

# Route for deployment pages
@app.route('/deployment')
def deployment():
    return render_template('deployment.html')

# Route for saving deployment configurations
@app.route('/save_deployment', methods=['POST'])
def save_deployment():
    vm_ip = request.form.get('vm_ip')
    username = request.form.get('username')
    password = request.form.get('password')
    data = {'vms': [{'ip': vm_ip, 'username': username, 'password': password}]}
    with open('deployment.json', 'w') as f:
        json.dump(data, f)
    return redirect(url_for('deployment'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)