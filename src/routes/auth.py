from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from models.models import db, AdminUser
import os

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            session.permanent = True
            flash("Logged in successfully!", "success")
            return redirect(url_for("admin.admin_env"))  # make sure this route exists
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))
