from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

db = SQLAlchemy()

# Admin Model
class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    bank_name = db.Column(db.String(100))
    account_title = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Owner Model
class Owner(UserMixin, db.Model):
    __tablename__ = 'owners'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    car_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rfid_card = db.Column(db.String(50), unique=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'))
    package_active = db.Column(db.Boolean, default=False)
    package_start_date = db.Column(db.DateTime)
    package_end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    package = db.relationship('Package', backref='owners')
    bookings = db.relationship('Booking', backref='owner', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Package Model
class Package(db.Model):
    __tablename__ = 'packages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Package Purchase Request Model
class PurchaseRequest(db.Model):
    __tablename__ = 'purchase_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False)
    payment_proof = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Relationships
    owner = db.relationship('Owner', backref='purchase_requests')
    package = db.relationship('Package', backref='purchase_requests')


# City Model
class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    regions = db.relationship('Region', backref='city', lazy=True, cascade='all, delete-orphan')


# Region Model
class Region(db.Model):
    __tablename__ = 'regions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subregions = db.relationship('SubRegion', backref='region', lazy=True, cascade='all, delete-orphan')


# SubRegion Model
class SubRegion(db.Model):
    __tablename__ = 'subregions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)
    gate_device_token = db.Column(db.String(8), unique=True)  # For ESP32-CAM gate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    slots = db.relationship('Slot', backref='subregion', lazy=True, cascade='all, delete-orphan')
    
    def generate_gate_token(self):
        """Generate unique 8-character gate device token"""
        self.gate_device_token = secrets.token_hex(4)  # Generates 8 hex characters


# Slot Model
class Slot(db.Model):
    __tablename__ = 'slots'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subregion_id = db.Column(db.Integer, db.ForeignKey('subregions.id'), nullable=False)
    device_token = db.Column(db.String(8), unique=True, nullable=False)
    status = db.Column(db.String(20), default='available')  # available, booked, occupied, offline
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='slot', lazy=True)
    
    def generate_device_token(self):
        """Generate unique 8-character device token"""
        self.device_token = secrets.token_hex(4)  # Generates 8 hex characters


# Booking Model
class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('slots.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)