import os
import datetime

from html_generator import generate_html
from models.models import db, Report  # Make sure Report is imported

# -----------------------------
# Save raw code as .txt
# -----------------------------
def save_code_to_file(code):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)

    filename = f"user_code_{timestamp}.txt"
    filepath = os.path.join(reports_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"\n✅ Code saved to {filepath}")
    return filepath, timestamp

# -----------------------------
# Save HTML analysis result
# -----------------------------
def save_html_output(code, dataset, analysis, timestamp, user_id=None):
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)

    output_filename = f"gemini_analysis_{timestamp}.html"
    output_path = os.path.join(reports_dir, output_filename)

    html_content = generate_html(code, dataset, analysis)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ Gemini analysis saved to {output_path}")

    # Save record in database
    report = Report(
        filename=output_filename,
        dataset=dataset,
        created_at=datetime.datetime.utcnow(),
        user_id=user_id  # Can be None if not authenticated
    )

    db.session.add(report)
    db.session.commit()

    print(f"🗃️  Report metadata saved to DB as {report.filename}")
    return output_filename
