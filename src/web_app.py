from flask import Flask, render_template, request, redirect, url_for, send_from_directory, render_template_string
from gemini_analyzer import analyze_with_gemini
from file_saver import save_code_to_file, save_html_output
import os
import time
import io
import sys
import traceback
from flask import jsonify

# Initialize Flask app with template directory
app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates")))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        dataset = request.form.get("dataset", "")
        code = request.form.get("code", "")

        # Save user code
        _, timestamp = save_code_to_file(code)

        # Analyze with Gemini
        analysis = analyze_with_gemini(code, dataset)

        # Save HTML report
        save_html_output(code, dataset, analysis, timestamp)

        # Redirect to result page with timestamp
        return redirect(url_for("result", ts=timestamp))

    return render_template("index.html")


@app.route("/result/<ts>")
def result(ts):
    report_name = f"gemini_analysis_{ts}.html"
    return render_template("result.html", report_name=report_name)



@app.route('/reports/<filename>')
def download_report(filename):
    reports_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    return send_from_directory(reports_path, filename)

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

        # Inject input size `n` into execution
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

@app.route("/benchmark", methods=["POST"])
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

if __name__ == "__main__":
    app.run(debug=True)
