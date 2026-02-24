from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({
        "message": "Hello, World!",
        "status": "success"
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Hello World API"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)