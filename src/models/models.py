from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_argon2 import Argon2

db = SQLAlchemy()
argon2 = Argon2()

class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = argon2.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        try:
            return argon2.check_password_hash(self.password_hash, password)
        except Exception:
            return False
