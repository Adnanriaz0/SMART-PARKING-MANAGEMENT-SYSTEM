import os
from datetime import timedelta

class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # MySQL Database configuration
    # Format: mysql+pymysql://username:password@host:port/database_name
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Adnan%4012%40@localhost:3306/smart_parking'
 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Upload folder for payment proofs
    UPLOAD_FOLDER = 'static/uploads/payment_proofs'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # Admin default credentials
    DEFAULT_ADMIN_EMAIL = 'admin@smartparking.com'
    DEFAULT_ADMIN_PASSWORD = 'admin123'