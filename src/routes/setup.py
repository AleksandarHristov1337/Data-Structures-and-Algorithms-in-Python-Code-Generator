import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models.models import db, argon2, AdminUser
from dotenv import load_dotenv, set_key
import psycopg2

setup_bp = Blueprint('setup', __name__)

SETUP_FLAG = ".setup_done"

# Setup enforcement: redirect all requests to setup page if not completed
@setup_bp.before_app_request
def check_setup():
    if not os.path.exists(SETUP_FLAG):
        # Allow setup page and static files without redirect
        if request.endpoint != 'setup.setup' and not request.path.startswith('/static'):
            logging.debug(f"Setup incomplete: redirecting {request.path} to setup page")
            return redirect(url_for('setup.setup'))

@setup_bp.route("/setup", methods=["GET", "POST"])
def setup():
    if os.path.exists(SETUP_FLAG):
        # Setup already done: redirect to login
        return redirect(url_for("auth.login"))

    error = None
    if request.method == "POST":
        admin_username = request.form.get("admin_username", "").strip()
        admin_password = request.form.get("admin_password", "").strip()
        db_name = request.form.get("db_name", "").strip()
        db_username = request.form.get("db_username", "postgres").strip()
        db_password = request.form.get("db_password", "").strip()

        if not all([admin_username, admin_password, db_name, db_username, db_password]):
            error = "All fields are required."
        else:
            # Test DB connection directly with psycopg2 for detailed error reporting
            try:
                logging.debug(f"Attempting DB connection with user '{db_username}' to DB '{db_name}'")
                conn = psycopg2.connect(
                    dbname=db_name,
                    user=db_username,
                    password=db_password,
                    host='localhost'
                )
                conn.close()
                logging.debug("Database connection successful.")
            except Exception as e:
                logging.error(f"psycopg2 connection failed: {e}")
                error = f"Database connection failed: {e}"
                return render_template("setup.html", error=error)

            # Compose SQLAlchemy DB URL
            db_url = f"postgresql+psycopg2://{db_username}:{db_password}@localhost/{db_name}"

            # Save DB URL to .env file
            env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
            set_key(env_path, "DATABASE_URL", db_url)

            # Reload env vars and update config
            load_dotenv(env_path)
            current_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

            # Reinitialize DB and create tables
            try:
                with current_app.app_context():
                    db.engine.dispose()
                    db.create_all()

                    # Check if admin user exists
                    if AdminUser.query.filter_by(username=admin_username).first():
                        error = "Admin username already exists."
                        return render_template("setup.html", error=error)

                    # Create admin user
                    hashed = argon2.generate_password_hash(admin_password)
                    admin = AdminUser(username=admin_username, password_hash=hashed)
                    db.session.add(admin)
                    db.session.commit()

                    # Create setup flag file to mark setup complete
                    with open(SETUP_FLAG, "w") as flag_file:
                        flag_file.write("done")

                    flash("Setup complete! Please log in.", "success")
                    return redirect(url_for("auth.login"))

            except Exception as e:
                logging.error(f"Database setup error: {e}")
                error = f"Database error: {e}"

    return render_template("setup.html", error=error)
