import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Explicit database path in instance directory
    instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(instance_dir, "75hard.db")}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
