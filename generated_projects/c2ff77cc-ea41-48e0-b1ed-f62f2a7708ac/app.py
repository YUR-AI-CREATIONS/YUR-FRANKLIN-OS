from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///todos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Create tables
with app.app_context():
    db.create_all()

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todos with optional filtering"""
    completed = request.args.get('completed')
    
    if completed is not None:
        completed_bool = completed.lower() == 'true'
        todos = Todo.query.filter_by(completed=completed_bool).all()
    else:
        todos = Todo.query.all()
    
    return jsonify([todo.to_dict() for todo in todos])

@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a specific todo by ID"""
    todo = Todo.query.get_or_404(todo_id)
    return jsonify(todo.to_dict())

@app.route('/api/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    todo = Todo(
        title=data['title'],
        description=data.get('description', ''),
        completed=data.get('completed', False)
    )
    
    db.session.add(todo)
    db.session.commit()
    
    return jsonify(todo.to_dict()), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update an existing todo"""
    todo = Todo.query.get_or_404(todo_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'completed' in data:
        todo.completed = data['completed']
    
    todo.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(todo.to_dict())

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo"""
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify({'message': 'Todo deleted successfully'}), 200

@app.route('/api/todos/<int:todo_id>/toggle', methods=['PATCH'])
def toggle_todo(todo_id):
    """Toggle completion status of a todo"""
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    todo.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(todo.to_dict())

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Todo not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)