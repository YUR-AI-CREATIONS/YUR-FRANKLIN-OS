from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whats_next.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@app.route('/')
def index():
    tasks = Task.query.filter_by(status='pending').order_by(
        Task.priority.desc(), Task.due_date.asc()
    ).all()
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        priority = request.form.get('priority', 'medium')
        due_date_str = request.form.get('due_date')
        
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        
        db.session.add(task)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    return render_template('add_task.html')

@app.route('/task/<int:task_id>')
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('task_detail.html', task=task)

@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if 'status' in request.json:
        task.status = request.json['status']
        db.session.commit()
        return jsonify({'success': True, 'task': task.to_dict()})
    
    return jsonify({'success': False, 'error': 'Invalid request'})

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/completed')
def completed_tasks():
    tasks = Task.query.filter_by(status='completed').order_by(
        Task.updated_at.desc()
    ).all()
    return render_template('completed.html', tasks=tasks)

@app.route('/api/next_task')
def api_next_task():
    """API endpoint to get the next most important task"""
    next_task = Task.query.filter_by(status='pending').order_by(
        Task.priority.desc(), Task.due_date.asc()
    ).first()
    
    if next_task:
        return jsonify({
            'success': True,
            'task': next_task.to_dict(),
            'message': "Here's what you should work on next!"
        })
    else:
        return jsonify({
            'success': False,
            'message': "No pending tasks! You're all caught up!"
        })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)