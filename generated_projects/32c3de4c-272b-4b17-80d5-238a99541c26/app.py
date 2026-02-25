from flask import Flask, request, jsonify
from decimal import Decimal, InvalidOperation
import math

app = Flask(__name__)

class Calculator:
    @staticmethod
    def add(a, b):
        return float(Decimal(str(a)) + Decimal(str(b)))
    
    @staticmethod
    def subtract(a, b):
        return float(Decimal(str(a)) - Decimal(str(b)))
    
    @staticmethod
    def multiply(a, b):
        return float(Decimal(str(a)) * Decimal(str(b)))
    
    @staticmethod
    def divide(a, b):
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return float(Decimal(str(a)) / Decimal(str(b)))
    
    @staticmethod
    def power(a, b):
        return float(pow(Decimal(str(a)), Decimal(str(b))))
    
    @staticmethod
    def sqrt(a):
        if a < 0:
            raise ValueError("Square root of negative number is not allowed")
        return float(math.sqrt(a))
    
    @staticmethod
    def sin(a):
        return float(math.sin(math.radians(a)))
    
    @staticmethod
    def cos(a):
        return float(math.cos(math.radians(a)))
    
    @staticmethod
    def tan(a):
        return float(math.tan(math.radians(a)))
    
    @staticmethod
    def log(a, base=math.e):
        if a <= 0:
            raise ValueError("Logarithm of non-positive number is not allowed")
        if base == math.e:
            return float(math.log(a))
        return float(math.log(a, base))

def validate_numbers(*args):
    try:
        return [float(arg) for arg in args]
    except (ValueError, TypeError):
        raise ValueError("All inputs must be valid numbers")

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Calculator API",
        "version": "1.0.0",
        "endpoints": {
            "POST /calculate": "Perform basic calculations",
            "POST /scientific": "Perform scientific calculations",
            "GET /health": "Health check"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        operation = data.get('operation')
        operands = data.get('operands', [])
        
        if not operation:
            return jsonify({"error": "Operation is required"}), 400
        
        if not operands or len(operands) < 1:
            return jsonify({"error": "At least one operand is required"}), 400
        
        calc = Calculator()
        
        if operation == 'add':
            if len(operands) < 2:
                return jsonify({"error": "Addition requires at least 2 operands"}), 400
            numbers = validate_numbers(*operands)
            result = numbers[0]
            for num in numbers[1:]:
                result = calc.add(result, num)
        
        elif operation == 'subtract':
            if len(operands) != 2:
                return jsonify({"error": "Subtraction requires exactly 2 operands"}), 400
            a, b = validate_numbers(*operands)
            result = calc.subtract(a, b)
        
        elif operation == 'multiply':
            if len(operands) < 2:
                return jsonify({"error": "Multiplication requires at least 2 operands"}), 400
            numbers = validate_numbers(*operands)
            result = numbers[0]
            for num in numbers[1:]:
                result = calc.multiply(result, num)
        
        elif operation == 'divide':
            if len(operands) != 2:
                return jsonify({"error": "Division requires exactly 2 operands"}), 400
            a, b = validate_numbers(*operands)
            result = calc.divide(a, b)
        
        else:
            return jsonify({"error": f"Unknown operation: {operation}"}), 400
        
        return jsonify({
            "operation": operation,
            "operands": operands,
            "result": result
        })
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/scientific', methods=['POST'])
def scientific():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        operation = data.get('operation')
        operands = data.get('operands', [])
        
        if not operation:
            return jsonify({"error": "Operation is required"}), 400
        
        calc = Calculator()
        
        if operation == 'power':
            if len(operands) != 2:
                return jsonify({"error": "Power requires exactly 2 operands"}), 400
            a, b = validate_numbers(*operands)
            result = calc.power(a, b)
        
        elif operation == 'sqrt':
            if len(operands) != 1:
                return jsonify({"error": "Square root requires exactly 1 operand"}), 400
            a = validate_numbers(operands[0])[0]
            result = calc.sqrt(a)
        
        elif operation == 'sin':
            if len(operands) != 1:
                return jsonify({"error": "Sine requires exactly 1 operand"}), 400
            a = validate_numbers(operands[0])[0]
            result = calc.sin(a)
        
        elif operation == 'cos':
            if len(operands) != 1:
                return jsonify({"error": "Cosine requires exactly 1 operand"}), 400
            a = validate_numbers(operands[0])[0]
            result = calc.cos(a)
        
        elif operation == 'tan':
            if len(operands) != 1:
                return jsonify({"error": "Tangent requires exactly 1 operand"}), 400
            a = validate_numbers(operands[0])[0]
            result = calc.tan(a)
        
        elif operation == 'log':
            if len(operands) == 1:
                a = validate_numbers(operands[0])[0]
                result = calc.log(a)
            elif len(operands) == 2:
                a, base = validate_numbers(*operands)
                result = calc.log(a, base)
            else:
                return jsonify({"error": "Logarithm requires 1 or 2 operands"}), 400
        
        else:
            return jsonify({"error": f"Unknown scientific operation: {operation}"}), 400
        
        return jsonify({
            "operation": operation,
            "operands": operands,
            "result": result
        })
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)