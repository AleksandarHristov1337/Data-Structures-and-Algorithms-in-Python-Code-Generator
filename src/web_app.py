from flask import Flask, render_template, request, redirect, url_for, send_from_directory, render_template_string
from gemini_analyzer import analyze_with_gemini
from file_saver import save_code_to_file, save_html_output
import os

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

if __name__ == "__main__":
    app.run(debug=True)
