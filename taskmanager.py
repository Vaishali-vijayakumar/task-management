from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tasks = db.relationship('Task', backref='author', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default='Medium')
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TaskMaster - Login</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <style>
            body { background-color: #f8f9fa; min-height: 100vh; display: flex; flex-direction: column; }
            .container { flex: 1; }
            .card { border-radius: 10px; border: none; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">TaskMaster</a>
            </div>
        </nav>

        <div class="container mt-4">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-4">
                    <div class="card shadow">
                        <div class="card-body">
                            <h2 class="card-title text-center mb-4">Login</h2>
                            <form method="POST" action="{{ url_for('login') }}">
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email</label>
                                    <input type="email" class="form-control" id="email" name="email" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Login</button>
                            </form>
                            <div class="mt-3 text-center">
                                <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="bg-light text-center text-lg-start mt-5">
            <div class="text-center p-3 bg-primary text-white">
                © 2023 TaskMaster - A Simple Task Management System
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            user = User(name=name, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TaskMaster - Register</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <style>
            body { background-color: #f8f9fa; min-height: 100vh; display: flex; flex-direction: column; }
            .container { flex: 1; }
            .card { border-radius: 10px; border: none; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">TaskMaster</a>
            </div>
        </nav>

        <div class="container mt-4">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-4">
                    <div class="card shadow">
                        <div class="card-body">
                            <h2 class="card-title text-center mb-4">Register</h2>
                            <form method="POST" action="{{ url_for('register') }}">
                                <div class="mb-3">
                                    <label for="name" class="form-label">Full Name</label>
                                    <input type="text" class="form-control" id="name" name="name" required>
                                </div>
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email</label>
                                    <input type="email" class="form-control" id="email" name="email" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                                <div class="mb-3">
                                    <label for="confirm_password" class="form-label">Confirm Password</label>
                                    <input type="password" class="form-control" id="confirm_password" name="confirm_password" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Register</button>
                            </form>
                            <div class="mt-3 text-center">
                                <p>Already have an account? <a href="{{ url_for('login') }}">Login here</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="bg-light text-center text-lg-start mt-5">
            <div class="text-center p-3 bg-primary text-white">
                © 2023 TaskMaster - A Simple Task Management System
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TaskMaster - Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <style>
            body { background-color: #f8f9fa; min-height: 100vh; display: flex; flex-direction: column; }
            .container { flex: 1; }
            .card { border-radius: 10px; border: none; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
            .table { background-color: white; border-radius: 10px; overflow: hidden; }
            .table th { background-color: #f8f9fa; font-weight: 600; }
            .badge { font-weight: 500; padding: 5px 10px; }
            .btn-group-sm .btn { padding: 0.25rem 0.5rem; font-size: 0.875rem; }
            .bg-danger { background-color: #dc3545 !important; }
            .bg-warning { background-color: #ffc107 !important; }
            .bg-secondary { background-color: #6c757d !important; }
            .bg-success { background-color: #198754 !important; }
            .bg-info { background-color: #0dcaf0 !important; }
            .table-hover tbody tr:hover { transform: translateY(-2px); transition: transform 0.2s; }
            @media (max-width: 768px) {
                .table-responsive { border: 0; }
                .table thead { display: none; }
                .table tr { display: block; margin-bottom: 1rem; border: 1px solid #dee2e6; border-radius: 10px; }
                .table td { display: block; text-align: right; padding-left: 50%; position: relative; border-bottom: 1px solid #dee2e6; }
                .table td::before { content: attr(data-label); position: absolute; left: 1rem; width: calc(50% - 1rem); padding-right: 1rem; text-align: left; font-weight: bold; }
                .table td:last-child { border-bottom: 0; }
                .btn-group { justify-content: flex-end; }
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">TaskMaster</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav me-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('new_task') }}">New Task</a>
                        </li>
                    </ul>
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <span class="nav-link">Hello, {{ current_user.name }}</span>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Your Tasks</h2>
                <a href="{{ url_for('new_task') }}" class="btn btn-primary">
                    <i class="bi bi-plus-circle"></i> Add Task
                </a>
            </div>

            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Task Summary</h5>
                            <div class="d-flex justify-content-between">
                                <div class="text-center">
                                    <h3>{{ tasks|length }}</h3>
                                    <p class="text-muted">Total Tasks</p>
                                </div>
                                <div class="text-center">
                                    <h3>{{ tasks|selectattr('status', 'equalto', 'Completed')|list|length }}</h3>
                                    <p class="text-muted">Completed</p>
                                </div>
                                <div class="text-center">
                                    <h3>{{ tasks|selectattr('status', 'equalto', 'Pending')|list|length }}</h3>
                                    <p class="text-muted">Pending</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {% if tasks %}
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Due Date</th>
                            <th>Priority</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for task in tasks %}
                        <tr class="{% if task.status == 'Completed' %}table-success{% elif task.due_date and task.due_date < datetime.utcnow() and task.status != 'Completed' %}table-danger{% endif %}">
                            <td>{{ task.title }}</td>
                            <td>{{ task.due_date.strftime('%Y-%m-%d') if task.due_date else 'No due date' }}</td>
                            <td>
                                <span class="badge 
                                    {% if task.priority == 'High' %}bg-danger
                                    {% elif task.priority == 'Medium' %}bg-warning text-dark
                                    {% else %}bg-secondary{% endif %}">
                                    {{ task.priority }}
                                </span>
                            </td>
                            <td>
                                <span class="badge 
                                    {% if task.status == 'Completed' %}bg-success
                                    {% else %}bg-info text-dark{% endif %}">
                                    {{ task.status }}
                                </span>
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    {% if task.status != 'Completed' %}
                                        <form action="{{ url_for('complete_task', task_id=task.id) }}" method="POST" class="d-inline">
                                            <button type="submit" class="btn btn-success btn-sm" title="Complete">
                                                <i class="bi bi-check-circle"></i>
                                            </button>
                                        </form>
                                    {% endif %}
                                    <a href="{{ url_for('edit_task', task_id=task.id) }}" class="btn btn-primary btn-sm" title="Edit">
                                        <i class="bi bi-pencil"></i>
                                    </a>
                                    <form action="{{ url_for('delete_task', task_id=task.id) }}" method="POST" class="d-inline">
                                        <button type="submit" class="btn btn-danger btn-sm" title="Delete" onclick="return confirm('Are you sure you want to delete this task?')">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="alert alert-info">
                You don't have any tasks yet. <a href="{{ url_for('new_task') }}" class="alert-link">Create your first task</a>.
            </div>
            {% endif %}
        </div>

        <footer class="bg-light text-center text-lg-start mt-5">
            <div class="text-center p-3 bg-primary text-white">
                © 2023 TaskMaster - A Simple Task Management System
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Set minimum date for due date fields to today
                var today = new Date().toISOString().split('T')[0];
                document.getElementById('due_date')?.setAttribute('min', today);
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        priority = request.form.get('priority')
        
        task = Task(
            title=title,
            description=description,
            due_date=datetime.strptime(due_date, '%Y-%m-%d') if due_date else None,
            priority=priority,
            status='Pending',
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TaskMaster - New Task</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <style>
            body { background-color: #f8f9fa; min-height: 100vh; display: flex; flex-direction: column; }
            .container { flex: 1; }
            .card { border-radius: 10px; border: none; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">TaskMaster</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav me-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('new_task') }}">New Task</a>
                        </li>
                    </ul>
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <span class="nav-link">Hello, {{ current_user.name }}</span>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card shadow">
                        <div class="card-body">
                            <h2 class="card-title mb-4">Create New Task</h2>
                            <form method="POST" action="{{ url_for('new_task') }}">
                                <div class="mb-3">
                                    <label for="title" class="form-label">Title</label>
                                    <input type="text" class="form-control" id="title" name="title" required>
                                </div>
                                <div class="mb-3">
                                    <label for="description" class="form-label">Description</label>
                                    <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="due_date" class="form-label">Due Date</label>
                                        <input type="date" class="form-control" id="due_date" name="due_date">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label for="priority" class="form-label">Priority</label>
                                        <select class="form-select" id="priority" name="priority">
                                            <option value="Low">Low</option>
                                            <option value="Medium" selected>Medium</option>
                                            <option value="High">High</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                    <a href="{{ url_for('dashboard') }}" class="btn btn-secondary me-md-2">Cancel</a>
                                    <button type="submit" class="btn btn-primary">Create Task</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="bg-light text-center text-lg-start mt-5">
            <div class="text-center p-3 bg-primary text-white">
                © 2023 TaskMaster - A Simple Task Management System
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Set minimum date for due date fields to today
                var today = new Date().toISOString().split('T')[0];
                document.getElementById('due_date').setAttribute('min', today);
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        due_date = request.form.get('due_date')
        task.due_date = datetime.strptime(due_date, '%Y-%m-%d') if due_date else None
        task.priority = request.form.get('priority')
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TaskMaster - Edit Task</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <style>
            body { background-color: #f8f9fa; min-height: 100vh; display: flex; flex-direction: column; }
            .container { flex: 1; }
            .card { border-radius: 10px; border: none; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="{{ url_for('dashboard') }}">TaskMaster</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav me-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('new_task') }}">New Task</a>
                        </li>
                    </ul>
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <span class="nav-link">Hello, {{ current_user.name }}</span>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card shadow">
                        <div class="card-body">
                            <h2 class="card-title mb-4">Edit Task</h2>
                            <form method="POST" action="{{ url_for('edit_task', task_id=task.id) }}">
                                <div class="mb-3">
                                    <label for="title" class="form-label">Title</label>
                                    <input type="text" class="form-control" id="title" name="title" value="{{ task.title }}" required>
                                </div>
                                <div class="mb-3">
                                    <label for="description" class="form-label">Description</label>
                                    <textarea class="form-control" id="description" name="description" rows="3">{{ task.description }}</textarea>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="due_date" class="form-label">Due Date</label>
                                        <input type="date" class="form-control" id="due_date" name="due_date" 
                                               value="{{ task.due_date.strftime('%Y-%m-%d') if task.due_date else '' }}">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label for="priority" class="form-label">Priority</label>
                                        <select class="form-select" id="priority" name="priority">
                                            <option value="Low" {% if task.priority == 'Low' %}selected{% endif %}>Low</option>
                                            <option value="Medium" {% if task.priority == 'Medium' %}selected{% endif %}>Medium</option>
                                            <option value="High" {% if task.priority == 'High' %}selected{% endif %}>High</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                    <a href="{{ url_for('dashboard') }}" class="btn btn-secondary me-md-2">Cancel</a>
                                    <button type="submit" class="btn btn-primary">Update Task</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="bg-light text-center text-lg-start mt-5">
            <div class="text-center p-3 bg-primary text-white">
                © 2023 TaskMaster - A Simple Task Management System
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Set minimum date for due date fields to today
                var today = new Date().toISOString().split('T')[0];
                document.getElementById('due_date').setAttribute('min', today);
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/task/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    
    task.status = 'Completed'
    db.session.commit()
    return redirect(url_for('dashboard'))

def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

if __name__ == '__main__':
    app.run(debug=True)