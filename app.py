from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nahor_secret_v4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brana_v4.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Tables ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email_or_phone = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    messages = db.relationship('Message', backref='group', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    sender = db.relationship('User', backref='messages')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    views = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref='posts')

@login_manager.user_loader
def load_user(user_id): return User.query.get(int(user_id))

with app.app_context(): db.create_all()

# --- Routes ---
@app.route('/')
def index(): return redirect(url_for('login'))

@app.route('/feed')
@login_required
def feed():
    posts = Post.query.order_by(Post.id.desc()).all()
    groups = Group.query.all()
    return render_template('feed.html', posts=posts, groups=groups)

@app.route('/create_group', methods=['POST'])
@login_required
def create_group():
    group_name = request.form.get('group_name')
    new_group = Group(name=group_name, creator_id=current_user.id)
    db.session.add(new_group)
    db.session.commit()
    return redirect(url_for('feed'))

@app.route('/chat/<int:group_id>', methods=['GET', 'POST'])
@login_required
def chat(group_id):
    group = Group.query.get_or_404(group_id)
    if request.method == 'POST':
        msg_content = request.form.get('message')
        new_msg = Message(content=msg_content, user_id=current_user.id, group_id=group_id)
        db.session.add(new_msg)
        db.session.commit()
    messages = Message.query.filter_by(group_id=group_id).all()
    return render_template('chat.html', group=group, messages=messages)

# (Login, Register and Post routes same as before...)

