from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# 1. USER TABLE
class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.user_id)

# 2. ADMIN TABLE
class Admin(db.Model, UserMixin):
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"admin_{self.admin_id}"

# 3. WATCHLIST TABLE
class Watchlist(db.Model):
    watchlist_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    ticker = db.Column(db.String(20), nullable=False)

# 4. HISTORY TABLE (Updated with Interval)
class History(db.Model):
    history_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    ticker = db.Column(db.String(20), nullable=False)
    signal = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    interval = db.Column(db.String(10), nullable=True)  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)