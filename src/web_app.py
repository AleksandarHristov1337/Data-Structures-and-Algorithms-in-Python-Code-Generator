from flask import Flask
from flask_login import LoginManager
from models.models import AdminUser
from werkzeug.security import generate_password_hash
import os, sys
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "templates")))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-default-dev-secret-key")
app.permanent_session_lifetime = timedelta(minutes=30)

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Admin user setup (can be from env)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", generate_password_hash("admin123"))
admin_user = AdminUser(id="1", username=ADMIN_USERNAME, password_hash=ADMIN_PASSWORD_HASH)

@login_manager.user_loader
def load_user(user_id):
    if user_id == admin_user.id:
        return admin_user
    return None

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

if __name__ == "__main__":
    app.run(debug=True)
