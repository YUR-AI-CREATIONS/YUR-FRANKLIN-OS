from app import app

if __name__ == '__main__':
    print("Starting Hello World API...")
    print("API will be available at: http://localhost:5000")
    print("Health check available at: http://localhost:5000/health")
    app.run(host='0.0.0.0', port=5000, debug=True)