from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('DailyProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Challenge(db.Model):
    __tablename__ = 'challenge'
    
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_current_day(self):
        """Calculate which day of the challenge we're on (1-75)"""
        if not self.is_active:
            return 0
        
        today = date.today()
        delta = (today - self.start_date).days + 1
        
        if delta < 1:
            return 0  # Challenge hasn't started yet
        elif delta > 75:
            return 75  # Challenge is complete
        else:
            return delta
    
    def __repr__(self):
        return f'<Challenge starting {self.start_date}>'

class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_text = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    progress = db.relationship('DailyProgress', backref='goal', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Goal {self.goal_text}>'

class DailyProgress(db.Model):
    __tablename__ = 'daily_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'goal_id', 'day_number', name='unique_user_goal_day'),
    )
    
    def __repr__(self):
        return f'<Progress Day {self.day_number} Goal {self.goal_id} User {self.user_id}>'
