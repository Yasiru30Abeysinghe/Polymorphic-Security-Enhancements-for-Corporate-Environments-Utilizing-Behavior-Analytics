from flask import Flask, request, jsonify, render_template
from elasticsearch import Elasticsearch
import urllib3

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Update this with your Elasticsearch host and credentials
es = Elasticsearch(
    ['http://localhost:9200'],  # Changed to http
    basic_auth=('elastic', 'changeme')  # Replace with your actual username and password
)

# Ensure the risk_coefficients index exists
def ensure_index():
    try:
        if not es.indices.exists(index="risk_coefficients"):
            es.indices.create(index="risk_coefficients", body={
                "mappings": {
                    "properties": {
                        "w1": {"type": "double"},
                        "w2": {"type": "double"},
                        "w3": {"type": "double"},
                        "w4": {"type": "double"},
                        "w5": {"type": "double"},
                        "w6": {"type": "double"},
                        "w7": {"type": "double"},
                        "w8": {"type": "double"},
                        "w9": {"type": "double"},
                        "w10": {"type": "double"}
                    }
                }
            })
            # Insert initial values
            es.index(index="risk_coefficients", id=1, body={
                "w1": 0.139650873, "w2": 0.19201995, "w3": 0.039900249,
                "w4": 0.089775561, "w5": 0.089775561, "w6": 0.144638404,
                "w7": 0.064837905, "w8": 0.064837905, "w9": 0.099750623,
                "w10": 0.074812968
            })
        print("Index 'risk_coefficients' exists or was created successfully.")
    except Exception as e:
        print(f"Error ensuring index: {str(e)}")

@app.route('/')
def index():
    try:
        coefficients = es.get(index="risk_coefficients", id=1)['_source']
        return render_template('index.html', coefficients=coefficients)
    except Exception as e:
        return f"Error fetching coefficients: {str(e)}", 500

@app.route('/update_coefficients', methods=['POST'])
def update_coefficients():
    try:
        new_coeffs = request.json
        es.index(index="risk_coefficients", id=1, body=new_coeffs)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    ensure_index()
    app.run(host='0.0.0.0', port=5000, debug=True)
