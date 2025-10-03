from flask import Flask
from flask_login import LoginManager
from models.models import db, AdminUser
from werkzeug.security import generate_password_hash
import os
from datetime import timedelta

# Initialize Flask app
app = Flask(
    __name__,
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-default-dev-secret-key")
app.permanent_session_lifetime = timedelta(minutes=30)

# Database configuration (using SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

# Register blueprints
from routes.main import main_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.analyze import analyze_bp
from routes.execute import execute_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(analyze_bp)
app.register_blueprint(execute_bp)

# Create the database and ensure default admin user exists
with app.app_context():
    db.create_all()

    default_admin = AdminUser.query.filter_by(username="admin").first()
    if not default_admin:
        default_admin = AdminUser(
            username="admin",
            password_hash=generate_password_hash("admin123")
        )
        db.session.add(default_admin)
        db.session.commit()
        print("✅ Default admin user created: admin / admin123")

if __name__ == "__main__":
    app.run(debug=True)
