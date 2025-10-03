from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from utils.env_utils import read_env, write_env

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin", methods=["GET", "POST"])
@login_required
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

    return render_template("admin.html", env=env_vars)
