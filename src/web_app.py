from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response, jsonify
from gemini_analyzer import analyze_with_gemini
from file_saver import save_code_to_file, save_html_output
import os
import time
import io
import sys
import traceback
import threading

# Initialize Flask app
app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates")))

# In-memory progress tracking
progress_tracker = {}
error_tracker = {}

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
            progress_tracker[timestamp] = 100  # mark complete
        except Exception as e:
            print("❌ Error during analysis:", e)
            error_tracker[timestamp] = str(e)
            progress_tracker[timestamp] = -1  # special marker for error

    threading.Thread(target=run_analysis).start()
    return redirect(url_for("progress_page", ts=timestamp))


@app.route("/progress/<ts>")
def progress(ts):
    def stream():
        while True:
            progress = progress_tracker.get(ts, 0)

            # Handle error
            if progress == -1:
                yield f"data: error\n\n"
                break

            yield f"data: {progress}\n\n"
            if progress >= 100:
                break

            time.sleep(0.5)

    return Response(stream(), mimetype='text/event-stream')

@app.route("/progress-page/<ts>")
def progress_page(ts):
    return render_template("progress.html", ts=ts)

@app.route("/result/<ts>")
def result(ts):
    report_name = f"gemini_analysis_{ts}.html"
    return render_template("result.html", report_name=report_name)

@app.route('/reports/<filename>')
def download_report(filename):
    reports_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    return send_from_directory(reports_path, filename)

@app.route("/error/<ts>")
def error(ts):
    message = error_tracker.get(ts, "Unknown error.")
    return render_template("error.html", message=message)

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
