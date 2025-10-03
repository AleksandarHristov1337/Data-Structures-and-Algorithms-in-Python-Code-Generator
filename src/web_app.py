# ========================================
# 📦 IMPORTS
# ========================================
import os
import io
import sys
import time
import threading
import traceback
import logging
from datetime import timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    send_from_directory, Response, jsonify, session, flash
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import check_password_hash, generate_password_hash

from gemini_analyzer import analyze_with_gemini
from file_saver import save_code_to_file, save_html_output
from models.models import AdminUser  # Assuming it's defined in models/models.py

# ========================================
# ⚙️ CONFIGURATION
# ========================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "templates"))
REPORTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "reports"))
ENV_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", ".env"))
LOG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "admin_changes.log"))

DEFAULT_ENV_CONTENT = """GOOGLE_API_KEY=AIzaSyDmMD15toEJsPTnTLD0QYvtBpdD54YDc7c
MODEL_NAME=gemini-2.0-flash-001
"""

app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-default-dev-secret-key")
app.permanent_session_lifetime = timedelta(minutes=30)

# ========================================
# 🔐 LOGIN MANAGER SETUP
# ========================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", generate_password_hash("admin123"))
admin_user = AdminUser(id="1", username=ADMIN_USERNAME, password_hash=ADMIN_PASSWORD_HASH)

@login_manager.user_loader
def load_user(user_id):
    return admin_user if user_id == admin_user.id else None

# ========================================
# 🔧 ENVIRONMENT VARIABLE HANDLING
# ========================================
def read_env():
    if not os.path.exists(ENV_PATH):
        with open(ENV_PATH, "w") as f:
            f.write(DEFAULT_ENV_CONTENT)

    with open(ENV_PATH, "r") as f:
        lines = f.readlines()

    env_dict = {}
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            key, value = line.strip().split("=", 1)
            env_dict[key] = value
    return env_dict

def write_env(env_dict):
    with open(ENV_PATH, "w") as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")

    user = current_user.username if current_user.is_authenticated else "unknown"
    logging.info(f"{user} updated .env to: {env_dict}")

# ========================================
# 📝 LOGGING
# ========================================
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ========================================
# 🧠 IN-MEMORY TRACKING
# ========================================
progress_tracker = {}
error_tracker = {}

# ========================================
# 👤 AUTH ROUTES
# ========================================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == admin_user.username and admin_user.check_password(password):
            login_user(admin_user)
            session.permanent = True
            flash("Logged in successfully!", "success")
            return redirect(url_for("admin_env"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

# ========================================
# 🔐 ADMIN PANEL
# ========================================
@app.route("/admin", methods=["GET", "POST"])
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

# ========================================
# 🌐 MAIN ROUTES
# ========================================
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/start-analysis", methods=["POST"])
def start_analysis():
    dataset = request.form.get("dataset", "")
    code = request.form.get("code", "")

    _, timestamp = save_code_to_file(code)

    def progress_callback(percent):
        progress_tracker[timestamp] = percent

    def run_analysis():
        try:
            analysis = analyze_with_gemini(code, dataset, progress_callback)
            save_html_output(code, dataset, analysis, timestamp)
            progress_tracker[timestamp] = 100
        except Exception as e:
            print("❌ Error during analysis:", e)
            error_tracker[timestamp] = str(e)
            progress_tracker[timestamp] = -1

    threading.Thread(target=run_analysis).start()
    return redirect(url_for("progress_page", ts=timestamp))

@app.route("/progress-page/<ts>")
def progress_page(ts):
    return render_template("progress.html", ts=ts)

@app.route("/progress/<ts>")
def progress(ts):
    def stream():
        while True:
            progress = progress_tracker.get(ts, 0)
            if progress == -1:
                yield "data: error\n\n"
                break
            yield f"data: {progress}\n\n"
            if progress >= 100:
                break
            time.sleep(0.5)

    return Response(stream(), mimetype="text/event-stream")

@app.route("/result/<ts>")
def result(ts):
    report_name = f"gemini_analysis_{ts}.html"
    return render_template("result.html", report_name=report_name)

@app.route("/error/<ts>")
def error(ts):
    message = error_tracker.get(ts, "Unknown error.")
    return render_template("error.html", message=message)

@app.route("/reports/<filename>")
def download_report(filename):
    return send_from_directory(REPORTS_DIR, filename)

# ========================================
# ⚙️ EXECUTION + BENCHMARK
# ========================================
@app.route("/execute", methods=["GET", "POST"])
def execute():
    result = None
    error = None
    execution_time = None
    code = ""
    n = 0

    if request.method == "POST":
        code = request.form.get("code", "")
        input_size = int(request.form.get("input_size", "0"))
        user_globals = {"n": input_size}

        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        start_time = time.time()
        try:
            exec(code, user_globals)
            result = redirected_output.getvalue()
        except Exception:
            error = traceback.format_exc()
        finally:
            sys.stdout = old_stdout
            execution_time = time.time() - start_time

    return render_template("execute.html", result=result, error=error, time=execution_time, code=code, n=n)

@app.route("/benchmark", methods=["POST"])
def benchmark():
    data = request.get_json()
    code = data["code"]
    n = data["n"]

    error = None
    execution_time = None

    try:
        redirected_output = sys.stdout = io.StringIO()
        start_time = time.time()
        exec_globals = {"n": n}
        exec(code, exec_globals)
        sys.stdout = sys.__stdout__
        execution_time = time.time() - start_time
    except Exception:
        error = traceback.format_exc()
        execution_time = 0.0
        sys.stdout = sys.__stdout__

    return jsonify({"time": execution_time, "error": error})

# ========================================
# 🚀 RUN APP
# ========================================
if __name__ == "__main__":
    app.run(debug=True)
