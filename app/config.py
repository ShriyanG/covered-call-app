# config.py
# Application configuration settings

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    DEBUG = os.environ.get('DEBUG', True)
    DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
