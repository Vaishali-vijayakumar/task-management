from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='pending')
    category = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.due_date).all()
    return render_template('index.html', user=user, tasks=tasks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d') if request.form['due_date'] else None
        priority = request.form['priority']
        category = request.form['category']
        
        new_task = Task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            category=category,
            user_id=user.id
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks'))
    
    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.due_date).all()
    return render_template('tasks.html', tasks=tasks)

@app.route('/task/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = Task.query.get_or_404(task_id)
    if task.user_id != session['user_id']:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('tasks'))
    
    if request.method == 'POST':
        task.status = request.form['status']
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks'))

@app.route('/task/delete/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = Task.query.get_or_404(task_id)
    if task.user_id != session['user_id']:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('tasks'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
