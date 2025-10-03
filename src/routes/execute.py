from flask import Blueprint, request, render_template, jsonify
import time
import io
import sys
import traceback

execute_bp = Blueprint("execute", __name__)

@execute_bp.route("/execute", methods=["GET", "POST"])
def execute():
    result = None
    error = None
    execution_time = None
    code = ""
    n = 0

    if request.method == "POST":
        code = request.form.get("code", "")
        input_size = int(request.form.get("input_size", "0"))

        user_globals = {'n': input_size}
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

@execute_bp.route("/benchmark", methods=["POST"])
def benchmark():
    data = request.get_json()
    code = data["code"]
    n = data["n"]

    result = None
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
