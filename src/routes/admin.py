import os
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app
)
from flask_login import login_required, current_user
from models.models import db, Report, AdminUser
from utils.env_utils import read_env, write_env

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# -------------------------------
# Decorator to restrict access to admin users
# -------------------------------
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            flash("Access denied.", "error")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper

# -------------------------------
# Environment Variable Editor
# -------------------------------
@admin_bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def admin_env():
    env_vars = read_env()

    if request.method == "POST":
        new_google_api_key = request.form.get("GOOGLE_API_KEY", "").strip()
        new_model_name = request.form.get("MODEL_NAME", "").strip()

        if new_google_api_key and new_model_name:
            env_vars["GOOGLE_API_KEY"] = new_google_api_key
            env_vars["MODEL_NAME"] = new_model_name
            write_env(env_vars)
            flash("Environment variables updated successfully!", "success")
        else:
            flash("Both fields are required.", "error")

        return redirect(url_for("admin.admin_env"))

    return render_template("admin.html", env=env_vars)

# -------------------------------
# Reports List (Admin Only)
# -------------------------------
@admin_bp.route("/reports")
@login_required
@admin_required
def list_reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template("admin_reports.html", reports=reports)

# -------------------------------
# Rename Report (Admin Only)
# -------------------------------
@admin_bp.route("/reports/<int:report_id>/rename", methods=["POST"])
@login_required
@admin_required
def rename_report(report_id):
    new_filename = request.form.get("new_filename", "").strip()

    if not new_filename:
        flash("Filename cannot be empty.", "error")
        return redirect(url_for("admin.list_reports"))

    # Append .html if not present
    if not new_filename.lower().endswith(".html"):
        new_filename += ".html"

    report = Report.query.get_or_404(report_id)
    reports_dir = os.path.abspath(os.path.join(current_app.root_path, "..", "reports"))
    old_path = os.path.join(reports_dir, report.filename)
    new_path = os.path.join(reports_dir, new_filename)

    if not os.path.exists(old_path):
        flash("Original file does not exist.", "error")
        return redirect(url_for("admin.list_reports"))

    if os.path.exists(new_path):
        flash("A file with that name already exists.", "error")
        return redirect(url_for("admin.list_reports"))

    try:
        os.rename(old_path, new_path)
    except Exception as e:
        flash(f"Error renaming file: {e}", "error")
        return redirect(url_for("admin.list_reports"))

    try:
        report.filename = new_filename
        db.session.commit()
        flash("Report renamed successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Database error: {e}", "error")

    return redirect(url_for("admin.list_reports"))

# -------------------------------
# Delete Report (Admin Only)
# -------------------------------
@admin_bp.route("/reports/<int:report_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)

    reports_dir = os.path.abspath(os.path.join(current_app.root_path, "..", "reports"))
    file_path = os.path.join(reports_dir, report.filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(report)
        db.session.commit()
        flash("Report deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting report: {e}", "error")

    return redirect(url_for("admin.list_reports"))
