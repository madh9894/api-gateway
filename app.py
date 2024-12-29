from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Microservices' base URLs
MICROSERVICES = {
    "summarizer": "http://summarizer:5003",
    "ar2en": "http://ar2en:5002",
    "en2ar": "http://en2ar:5001"
}

@app.route('/<service>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway(service, path=""):
    if service not in MICROSERVICES:
        return jsonify({"error": "Service not found"}), 404

    url = f"{MICROSERVICES[service]}/{path}"
    method = request.method
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
    data = request.get_json() if request.data else None

    try:
        response = requests.request(method, url, headers=headers, json=data)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Service unavailable", "details": str(e)}), 503

# Handle root requests gracefully
@app.route('/')
def root():
    return jsonify({"message": "API Gateway is running", "available_services": list(MICROSERVICES.keys())})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
