from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.security import generate_password_hash
from models.models import AdminUser

auth_bp = Blueprint("auth", __name__)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", generate_password_hash("admin123"))
admin_user = AdminUser(id="1", username=ADMIN_USERNAME, password_hash=ADMIN_PASSWORD_HASH)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == admin_user.username and admin_user.check_password(password):
            login_user(admin_user)
            session.permanent = True
            flash("Logged in successfully!", "success")
            return redirect(url_for("admin.admin_env"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))
