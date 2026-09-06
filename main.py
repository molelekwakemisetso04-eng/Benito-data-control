from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Kemisetso's Betway Predictor API is running!"

@app.route('/predict', methods=['GET'])
def predict():
    count = int(request.args.get('count', 20))
    # Return your predictions as JSON data
    return jsonify({"count": count, "author": "Kemisetso", "status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
