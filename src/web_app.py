import os
from flask import Flask
from flask_login import LoginManager
from models.models import db, argon2, AdminUser
from dotenv import load_dotenv

def create_env_file():
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write(
                "GOOGLE_API_KEY=your_api_key_here\n"
                "MODEL_NAME=gemini-2.0-flash-001\n"
                "FLASK_SECRET_KEY=your_secret_key\n"
                "DATABASE_URL=\n"
                "SUPERUSER_PASSWORD=new_password\n"
            )
        print(f".env file created at {env_path}")
    else:
        print(f".env file already exists at {env_path}")

def create_app():
    create_env_file()

    # Load .env two levels up
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    load_dotenv(dotenv_path=env_path)

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "change_this_in_production")

    # Delay DB init if DATABASE_URL not present
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        print(f"✅ Using DATABASE_URL: {database_url}")
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        db.init_app(app)
    else:
        print("⚠️ No DATABASE_URL found — database setup will run first.")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    argon2.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return AdminUser.query.get(int(user_id))

    # Register blueprints
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
