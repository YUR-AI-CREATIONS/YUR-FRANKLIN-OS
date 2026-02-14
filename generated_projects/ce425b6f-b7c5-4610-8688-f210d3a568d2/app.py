from flask import Flask, render_template, request, jsonify, session
import openai
import os
from datetime import datetime, timedelta
import json
import sqlite3
import hashlib
import secrets
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database setup
def init_db():
    conn = sqlite3.connect('content_station.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS content
                 (id INTEGER PRIMARY KEY, user_id INTEGER, platform TEXT, 
                  content TEXT, hashtags TEXT, scheduled_time TEXT, 
                  created_at TEXT, status TEXT,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS templates
                 (id INTEGER PRIMARY KEY, name TEXT, template TEXT, category TEXT)''')
    
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect('content_station.db')
    c = conn.cursor()
    c.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    
    if user and hashlib.sha256(password.encode()).hexdigest() == user[1]:
        session['user_id'] = user[0]
        session['username'] = username
        return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect('content_station.db')
    c = conn.cursor()
    
    try:
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                 (username, password_hash))
        conn.commit()
        user_id = c.lastrowid
        session['user_id'] = user_id
        session['username'] = username
        conn.close()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username already exists'}), 400

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/generate-content', methods=['POST'])
@login_required
def generate_content():
    data = request.json
    platform = data.get('platform', 'general')
    topic = data.get('topic', '')
    tone = data.get('tone', 'casual')
    content_type = data.get('content_type', 'post')
    
    # Simulated AI content generation (replace with actual AI service)
    content_templates = {
        'instagram': {
            'casual': [
                f"Just discovered something amazing about {topic}! ✨ Who else is into this? Drop your thoughts below! 👇",
                f"Monday motivation: {topic} is giving me all the inspiration I need today! 💪 What's motivating you?",
                f"Can we talk about {topic} for a second? This has completely changed my perspective! 🤯"
            ],
            'professional': [
                f"Insights on {topic}: Key trends and implications for industry professionals.",
                f"Breaking down {topic}: What every professional should know in 2024.",
                f"Expert analysis: How {topic} is reshaping the business landscape."
            ]
        },
        'twitter': {
            'casual': [
                f"Hot take: {topic} is about to change everything 🔥 #trending",
                f"Me: *sees {topic}* Also me: *immediately becomes obsessed* 😅",
                f"PSA: If you're not following {topic}, you're missing out! Just saying 🤷‍♀️"
            ],
            'professional': [
                f"Industry insight: {topic} presents significant opportunities for growth and innovation.",
                f"Data shows {topic} is driving major shifts in consumer behavior. Thoughts?",
                f"Strategic implications of {topic} for business leaders in 2024."
            ]
        },
        'linkedin': {
            'professional': [
                f"Reflecting on recent developments in {topic} and their impact on our industry...",
                f"Three key takeaways from the latest {topic} research that every professional should consider:",
                f"Leadership perspective: How {topic} is creating new opportunities for innovation and growth."
            ]
        }
    }
    
    # Generate hashtags
    hashtag_suggestions = {
        'instagram': ['#contentcreator', '#socialmedia', '#trending', '#viral', '#inspiration'],
        'twitter': ['#trending', '#viral', '#socialmedia', '#content'],
        'linkedin': ['#professional', '#business', '#industry', '#leadership', '#innovation']
    }
    
    template_list = content_templates.get(platform, content_templates['instagram'])
    tone_templates = template_list.get(tone, template_list['casual'])
    
    import random
    generated_content = random.choice(tone_templates)
    suggested_hashtags = random.sample(hashtag_suggestions.get(platform, hashtag_suggestions['instagram']), 3)
    
    return jsonify({
        'content': generated_content,
        'hashtags': ' '.join(suggested_hashtags),
        'platform': platform,
        'character_count': len(generated_content)
    })

@app.route('/save-content', methods=['POST'])
@login_required
def save_content():
    data = request.json
    platform = data.get('platform')
    content = data.get('content')
    hashtags = data.get('hashtags', '')
    scheduled_time = data.get('scheduled_time', '')
    
    conn = sqlite3.connect('content_station.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO content 
                 (user_id, platform, content, hashtags, scheduled_time, created_at, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
             (session['user_id'], platform, content, hashtags, scheduled_time,
              datetime.now().isoformat(), 'draft'))
    
    conn.commit()
    content_id = c.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'content_id': content_id})

@app.route('/get-content')
@login_required
def get_content():
    conn = sqlite3.connect('content_station.db')
    c = conn.cursor()
    
    c.execute('''SELECT id, platform, content, hashtags, scheduled_time, created_at, status
                 FROM content WHERE user_id = ? ORDER BY created_at DESC''',
             (session['user_id'],))
    
    content_list = []
    for row in c.fetchall():
        content_list.append({
            'id': row[0],
            'platform': row[1],
            'content': row[2],
            'hashtags': row[3],
            'scheduled_time': row[4],
            'created_at': row[5],
            'status': row[6]
        })
    
    conn.close()
    return jsonify({'content': content_list})

@app.route('/delete-content/<int:content_id>', methods=['DELETE'])
@login_required
def delete_content(content_id):
    conn = sqlite3.connect('content_station.db')
    c = conn.cursor()
    
    c.execute('DELETE FROM content WHERE id = ? AND user_id = ?',
             (content_id, session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/analytics')
@login_required
def analytics():
    conn = sqlite3.connect('content_station.db')
    c = conn.cursor()
    
    # Get content stats
    c.execute('''SELECT platform, COUNT(*) as count FROM content 
                 WHERE user_id = ? GROUP BY platform''', (session['user_id'],))
    platform_stats = dict(c.fetchall())
    
    c.execute('''SELECT status, COUNT(*) as count FROM content 
                 WHERE user_id = ? GROUP BY status''', (session['user_id'],))
    status_stats = dict(c.fetchall())
    
    c.execute('''SELECT DATE(created_at) as date, COUNT(*) as count FROM content 
                 WHERE user_id = ? AND created_at >= date('now', '-30 days')
                 GROUP BY DATE(created_at) ORDER BY date''', (session['user_id'],))
    daily_stats = c.fetchall()
    
    conn.close()
    
    return jsonify({
        'platform_stats': platform_stats,
        'status_stats': status_stats,
        'daily_stats': daily_stats
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)