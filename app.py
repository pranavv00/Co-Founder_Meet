from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from github import Github

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///founder_connect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(20))  # 'founder' or 'developer'
    name = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    github_username = db.Column(db.String(100))
    portfolio_url = db.Column(db.String(200))
    ideas = db.relationship('Idea', backref='founder', lazy=True)
    applications = db.relationship('Application', backref='developer', lazy=True)

class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    equity_offered = db.Column(db.Float, nullable=False)
    salary_range = db.Column(db.String(50), nullable=False)
    founder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('Application', backref='idea', lazy=True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    developer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    idea_id = db.Column(db.Integer, db.ForeignKey('idea.id'), nullable=False)
    proposal = db.Column(db.Text, nullable=False)
    equity_ask = db.Column(db.Float, nullable=False)
    salary_ask = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    ideas = Idea.query.order_by(Idea.created_at.desc()).all()
    return render_template('index.html', ideas=ideas)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        name = request.form.get('name')
        whatsapp = request.form.get('whatsapp')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            user_type=user_type,
            name=name,
            whatsapp=whatsapp
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create_idea', methods=['GET', 'POST'])
@login_required
def create_idea():
    if current_user.user_type != 'founder':
        flash('Only founders can create ideas')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        idea = Idea(
            title=request.form.get('title'),
            description=request.form.get('description'),
            equity_offered=float(request.form.get('equity_offered')),
            salary_range=request.form.get('salary_range'),
            founder_id=current_user.id
        )
        db.session.add(idea)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('create_idea.html')

@app.route('/apply/<int:idea_id>', methods=['GET', 'POST'])
@login_required
def apply(idea_id):
    if current_user.user_type != 'developer':
        flash('Only developers can apply to ideas')
        return redirect(url_for('index'))
    
    idea = Idea.query.get_or_404(idea_id)
    
    if request.method == 'POST':
        application = Application(
            developer_id=current_user.id,
            idea_id=idea_id,
            proposal=request.form.get('proposal'),
            equity_ask=float(request.form.get('equity_ask')),
            salary_ask=float(request.form.get('salary_ask'))
        )
        db.session.add(application)
        db.session.commit()
        flash('Application submitted successfully')
        return redirect(url_for('index'))
    
    return render_template('apply.html', idea=idea)

@app.route('/applications/<int:idea_id>')
@login_required
def view_applications(idea_id):
    idea = Idea.query.get_or_404(idea_id)
    if current_user.id != idea.founder_id:
        flash('You can only view applications for your own ideas')
        return redirect(url_for('index'))
    
    return render_template('applications.html', idea=idea)

@app.route('/accept_application/<int:app_id>')
@login_required
def accept_application(app_id):
    application = Application.query.get_or_404(app_id)
    if current_user.id != application.idea.founder_id:
        flash('Unauthorized action')
        return redirect(url_for('index'))
    
    application.status = 'accepted'
    db.session.commit()
    flash('Application accepted! WhatsApp contact shared.')
    return redirect(url_for('view_applications', idea_id=application.idea_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
