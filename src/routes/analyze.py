from flask import Blueprint, request, redirect, url_for, render_template, Response
from gemini_analyzer import analyze_with_gemini
from file_saver import save_code_to_file, save_html_output
import threading
import time

analyze_bp = Blueprint("analyze", __name__)

progress_tracker = {}
error_tracker = {}

@analyze_bp.route("/start-analysis", methods=["POST"])
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
    return redirect(url_for("analyze.progress_page", ts=timestamp))

@analyze_bp.route("/progress/<ts>")
def progress(ts):
    def stream():
        while True:
            progress = progress_tracker.get(ts, 0)
            if progress == -1:
                yield f"data: error\n\n"
                break
            yield f"data: {progress}\n\n"
            if progress >= 100:
                break
            time.sleep(0.5)

    return Response(stream(), mimetype='text/event-stream')

@analyze_bp.route("/progress-page/<ts>")
def progress_page(ts):
    return render_template("progress.html", ts=ts)

@analyze_bp.route("/result/<ts>")
def result(ts):
    report_name = f"gemini_analysis_{ts}.html"
    return render_template("result.html", report_name=report_name)

@analyze_bp.route("/reports/<filename>")
def download_report(filename):
    from flask import send_from_directory
    import os
    reports_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    return send_from_directory(reports_path, filename)

@analyze_bp.route("/error/<ts>")
def error(ts):
    message = error_tracker.get(ts, "Unknown error.")
    return render_template("error.html", message=message)
