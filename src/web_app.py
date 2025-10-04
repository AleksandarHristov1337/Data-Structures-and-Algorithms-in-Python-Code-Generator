import os
from flask import Flask
from flask_login import LoginManager
from models.models import db, argon2, AdminUser
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)

    load_dotenv()

    app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "change_this_in_production")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:password@localhost:5432/mydatabase"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    argon2.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    from routes.setup import setup_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.analyze import analyze_bp
    from routes.execute import execute_bp
    from routes.main import main_bp

    app.register_blueprint(setup_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(execute_bp)
    app.register_blueprint(main_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
