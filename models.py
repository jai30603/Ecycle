import enum
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask_login import UserMixin


# ── Enumerations ─────────────────────────────────────────────────────────────

class OrganizationType(enum.Enum):
    OFFICE = "OFFICE"
    SCHOOL = "SCHOOL"
    COLLEGE = "COLLEGE"
    GOVERNMENT = "GOVERNMENT"
    NON_PROFIT = "NON_PROFIT"
    HEALTHCARE = "HEALTHCARE"
    OTHER = "OTHER"

class EwasteCondition(enum.Enum):
    WORKING = "WORKING"
    DAMAGED = "DAMAGED"
    SCRAP = "SCRAP"

class BulkPickupStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    COLLECTED = "COLLECTED"
    REJECTED = "REJECTED"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    eco_points = db.Column(db.Integer, default=0)
    carbon_saved = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pickups = db.relationship('Schedule', backref='user', lazy=True)
    ewaste_items = db.relationship('Ewaste', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ewaste(db.Model):
    __tablename__ = 'ewaste'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ewaste_type = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100))
    ram = db.Column(db.String(50))
    condition = db.Column(db.String(50))
    estimated_price = db.Column(db.Integer)
    eco_points = db.Column(db.Integer, default=0)
    classification_result = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    schedules = db.relationship('Schedule', backref='ewaste', lazy=True)

class Schedule(db.Model):
    __tablename__ = 'schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ewaste_id = db.Column(db.Integer, db.ForeignKey('ewaste.id'), nullable=False)
    pickup_date = db.Column(db.DateTime, nullable=False)
    pickup_address = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Collected
    scheduled_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ewaste_id': self.ewaste_id,
            'pickup_date': self.pickup_date.strftime('%Y-%m-%d %H:%M'),
            'pickup_address': self.pickup_address,
            'status': self.status,
            'scheduled_at': self.scheduled_at.strftime('%Y-%m-%d %H:%M'),
            'ewaste_type': self.ewaste.ewaste_type,
            'model': self.ewaste.model,
            'estimated_price': self.ewaste.estimated_price
        }

class Reward(db.Model):
    __tablename__ = 'rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    points_required = db.Column(db.Integer, nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)  # Product, Coupon, Discount
    stock = db.Column(db.Integer, default=10)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with redemptions
    redemptions = db.relationship('Redemption', backref='reward', lazy=True)
    
class Redemption(db.Model):
    __tablename__ = 'redemptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('rewards.id'), nullable=False)
    points_spent = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Processed, Delivered
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='redemptions', lazy=True)


# ── Bulk Pickup Models ────────────────────────────────────────────────────────

class BulkPickup(db.Model):
    __tablename__ = 'bulk_pickups'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_name = db.Column(db.String(100), nullable=False)
    organization_type = db.Column(db.String(50), nullable=False)  # OrganizationType enum value
    contact_person = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    gstin = db.Column(db.String(20))
    pickup_address = db.Column(db.Text, nullable=False)
    preferred_pickup_date = db.Column(db.DateTime, nullable=False)
    special_instructions = db.Column(db.Text)
    status = db.Column(db.String(20), default='PENDING')  # BulkPickupStatus enum value
    total_items = db.Column(db.Integer, default=0)
    total_eco_points = db.Column(db.Integer, default=0)
    request_certificate = db.Column(db.Boolean, default=False)
    request_tax_receipt = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='bulk_pickups', lazy=True)
    items = db.relationship('BulkEwasteItem', backref='bulk_pickup', lazy=True, cascade='all, delete-orphan')


class BulkEwasteItem(db.Model):
    __tablename__ = 'bulk_ewaste_items'

    id = db.Column(db.Integer, primary_key=True)
    bulk_pickup_id = db.Column(db.Integer, db.ForeignKey('bulk_pickups.id'), nullable=False)
    ewaste_type = db.Column(db.String(50), nullable=False)
    brand_model = db.Column(db.String(100))
    quantity = db.Column(db.Integer, default=1)
    condition = db.Column(db.String(20), default='WORKING')  # EwasteCondition enum value
    additional_notes = db.Column(db.Text)
    estimated_price_per_unit = db.Column(db.Integer, default=0)
    eco_points_per_unit = db.Column(db.Integer, default=0)
    image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── Community E-Talk Message ──────────────────────────────────────────────────

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref='messages', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'content': self.content,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%b %d, %H:%M') if self.created_at else 'Just now',
            'timestamp': int(self.created_at.timestamp()) if self.created_at else 0
        }

