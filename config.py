import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///library.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # === Flask-Mail settings ===
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'alexey.bobruiko@gmail.com'
    MAIL_PASSWORD = 'mwfy yugf fofs napy'
    MAIL_DEFAULT_SENDER = 'alexey.bobruiko@gmail.com'