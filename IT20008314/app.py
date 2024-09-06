from flask import Flask, request, jsonify
from phishing_detection import check_domain  # Import your phishing detection code

app = Flask(__name__)

#@app.route('/')
#def home():
    #return "Welcome to the Phishing Detection API. Use /check_domain to check domains."

@app.route('/check_domain', methods=['POST'])
def check_domain_endpoint():
    data = request.json
    domain = data.get('domain')
    if not domain:
        return jsonify({"error": "No domain provided"}), 400
    
    risk_status = check_domain(domain)
    return jsonify({"domain": domain, "risk_status": risk_status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
