import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models.models import db, argon2, AdminUser
from dotenv import load_dotenv, set_key
import psycopg2

setup_bp = Blueprint('setup', __name__)

SETUP_FLAG = ".setup_done"

@setup_bp.before_app_request
def check_setup():
    if not os.path.exists(SETUP_FLAG):
        if request.endpoint != 'setup.setup' and not request.path.startswith('/static'):
            logging.debug(f"Setup incomplete: redirecting {request.path} to setup page")
            return redirect(url_for('setup.setup'))
    else:
        if not AdminUser.query.first():
            logging.warning("Setup flag present but no admin user found. Resetting setup.")
            os.remove(SETUP_FLAG)
            flash("No admin user found. Please complete setup again.", "warning")
            return redirect(url_for('setup.setup'))

@setup_bp.route("/setup", methods=["GET", "POST"])
def setup():
    if os.path.exists(SETUP_FLAG):
        return redirect(url_for("auth.login"))

    error = None
    if request.method == "POST":
        admin_username = request.form.get("admin_username", "").strip()
        admin_password = request.form.get("admin_password", "").strip()
        db_name = request.form.get("db_name", "").strip()
        db_password = request.form.get("db_password", "").strip()

        if not all([admin_username, admin_password, db_name, db_password]):
            error = "All fields are required."
            return render_template("setup.html", error=error)

        # Fixed DB username
        db_username = "postgres"

        try:
            superuser_password = os.getenv("SUPERUSER_PASSWORD", "new_password")

            # Connect as superuser to Postgres
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres',
                password=superuser_password,
                host='localhost'
            )
            conn.autocommit = True
            cur = conn.cursor()

            # Update password for fixed user
            cur.execute(f"ALTER USER {db_username} WITH PASSWORD %s", (db_password,))

            # Create database if not exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if not cur.fetchone():
                cur.execute(f"CREATE DATABASE {db_name} OWNER {db_username}")
                logging.info(f"Database '{db_name}' created.")
            else:
                logging.info(f"Database '{db_name}' already exists.")

            cur.close()
            conn.close()

            # Compose DB URL for SQLAlchemy
            db_url = f"postgresql+psycopg2://{db_username}:{db_password}@localhost/{db_name}"
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
            set_key(env_path, "DATABASE_URL", db_url)

            load_dotenv(env_path)
            current_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

            with current_app.app_context():
                db.engine.dispose()
                db.create_all()

                if AdminUser.query.filter_by(username=admin_username).first():
                    error = "Admin username already exists."
                    return render_template("setup.html", error=error)

                hashed = argon2.generate_password_hash(admin_password)
                admin = AdminUser(username=admin_username, password_hash=hashed, is_admin=True)
                db.session.add(admin)
                db.session.commit()

                with open(SETUP_FLAG, "w") as flag_file:
                    flag_file.write("done")

                flash("Setup complete! Please log in.", "success")
                return redirect(url_for("auth.login"))

        except Exception as e:
            logging.error(f"Setup failed: {e}")
            error = f"Setup failed: {e}"

    return render_template("setup.html", error=error)
