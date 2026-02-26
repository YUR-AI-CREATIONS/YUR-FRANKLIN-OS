# neural_net_simple.py
import random
import math

# Sigmoid activation function
def sigmoid(x):
    return 1 / (1 + math.exp(-x))

# Derivative of sigmoid
def sigmoid_derivative(x):
    return x * (1 - x)

# Initialize weights and biases with random values
def initialize_weights(input_size, hidden_size, output_size):
    weights1 = [[random.uniform(-1, 1) for _ in range(hidden_size)] for _ in range(input_size)]
    weights2 = [[random.uniform(-1, 1) for _ in range(output_size)] for _ in range(hidden_size)]
    bias1 = [random.uniform(-1, 1) for _ in range(hidden_size)]
    bias2 = [random.uniform(-1, 1) for _ in range(output_size)]
    return weights1, weights2, bias1, bias2

# Matrix multiplication
def matrix_multiply(matrix, vector):
    result = []
    for row in matrix:
        sum_val = 0
        for i in range(len(vector)):
            sum_val += row[i] * vector[i]
        result.append(sum_val)
    return result

# Vector addition
def vector_add(vector1, vector2):
    return [v1 + v2 for v1, v2 in zip(vector1, vector2)]

# Element-wise multiplication for vectors
def vector_multiply(vector, scalar):
    return [v * scalar for v in vector]

# Forward propagation
def forward_propagation(inputs, weights1, weights2, bias1, bias2):
    hidden = vector_add(matrix_multiply(weights1, inputs), bias1)
    hidden = [sigmoid(x) for x in hidden]
    output = vector_add(matrix_multiply(weights2, hidden), bias2)
    output = [sigmoid(x) for x in output]
    return hidden, output

# Backpropagation
def backpropagation(inputs, hidden, output, target, weights1, weights2, bias1, bias2, learning_rate):
    output_errors = [(target[i] - output[i]) * sigmoid_derivative(output[i]) for i in range(len(output))]
    hidden_errors = []
    for i in range(len(hidden)):
        error = 0
        for j in range(len(output_errors)):
            error += output_errors[j] * weights2[i][j]
        hidden_errors.append(error * sigmoid_derivative(hidden[i]))

    # Update weights2 and bias2
    for i in range(len(weights2)):
        for j in range(len(weights2[0])):  # Use weights2[0] to get output_size
            weights2[i][j] += learning_rate * output_errors[j] * hidden[i]
    for j in range(len(bias2)):
        bias2[j] += learning_rate * output_errors[j]

    # Update weights1 and bias1
    for i in range(len(weights1)):
        for j in range(len(weights1[0])):  # Use weights1[0] to get hidden_size
            weights1[i][j] += learning_rate * hidden_errors[j] * inputs[i]
    for j in range(len(bias1)):
        bias1[j] += learning_rate * hidden_errors[j]

    return weights1, weights2, bias1, bias2

# Mean squared error loss
def calculate_loss(output, target):
    return sum([(target[i] - output[i]) ** 2 for i in range(len(output))]) / len(output)

def main():
    # Network configuration
    input_size = 2
    hidden_size = 4
    output_size = 1
    learning_rate = 0.1
    epochs = 20

    # Dummy data (XOR problem)
    training_data = [
        ([0, 0], [0]),
        ([0, 1], [1]),
        ([1, 0], [1]),
        ([1, 1], [0])
    ]

    # Initialize network
    weights1, weights2, bias1, bias2 = initialize_weights(input_size, hidden_size, output_size)

    print("Training started...")
    for epoch in range(epochs):
        total_loss = 0
        for inputs, target in training_data:
            # Forward pass
            hidden, output = forward_propagation(inputs, weights1, weights2, bias1, bias2)
            total_loss += calculate_loss(output, target)
            # Backward pass
            weights1, weights2, bias1, bias2 = backpropagation(
                inputs, hidden, output, target, weights1, weights2, bias1, bias2, learning_rate
            )
        avg_loss = total_loss / len(training_data)
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.6f}")

    print("\nTesting the network:")
    for inputs, target in training_data:
        _, output = forward_propagation(inputs, weights1, weights2, bias1, bias2)
        print(f"Input: {inputs}, Target: {target}, Output: {[round(o, 2) for o in output]}")

if __name__ == "__main__":
    main()