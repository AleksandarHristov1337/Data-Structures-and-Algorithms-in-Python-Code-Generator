from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_argon2 import Argon2
from datetime import datetime

db = SQLAlchemy()
argon2 = Argon2()

class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = argon2.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        try:
            return argon2.check_password_hash(self.password_hash, password)
        except Exception:
            return False

class User(UserMixin, db.Model):  # Keep UserMixin before db.Model for clarity
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    reports = db.relationship("Report", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = argon2.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        try:
            return argon2.check_password_hash(self.password_hash, password)
        except Exception:
            return False

class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    dataset = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_by_admin = db.Column(db.Boolean, default=False)  # NEW FIELD

    def __repr__(self):
        return f"<Report {self.filename}>"
