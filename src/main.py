import datetime
import os
import google.generativeai as genai
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=dotenv_path)

# Configure Gemini API
MODEL_NAME = os.getenv("MODEL_NAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Get user input
def get_user_input():
    dataset = input("Enter your dataset (comma-separated or JSON-like format):\n")
    print("\nEnter your Python code below. Type 'END' on a new line to finish:\n")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    user_code = "\n".join(lines)
    return dataset, user_code

# Save user code to .txt file
def save_code_to_file(code):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    filename = f"user_code_{timestamp}.txt"
    filepath = os.path.join(reports_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"\n✅ Code saved to {filepath}")
    return filepath, timestamp

# Analyze code with Gemini
def analyze_with_gemini(code, dataset):
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = f"""
You are a Python performance expert.

Analyze the following code and dataset:

Dataset:
{dataset}

Code:
{code}

Tasks:
1. Identify and list all data structures used.
2. Categorize them by time complexity:
   - Fastest
   - Average
   - Slowest
3. Explain how the algorithm works (briefly).
4. Provide Big-O time and space complexities.
5. Suggest more efficient alternatives if possible.
6. Print the optimized code with improvements.
"""

    print("\n⏳ Sending code to Gemini for analysis...\n")
    response = model.generate_content(prompt)
    print("\n📊 Gemini Analysis Output:\n")
    print(response.text)
    return response.text

# Save output to HTML (escaped)
import html
import markdown2

def save_html_output(code, dataset, analysis, timestamp):
    import html
    import markdown2

    escaped_code = html.escape(code)
    escaped_dataset = html.escape(dataset)
    formatted_analysis = markdown2.markdown(analysis, extras=["fenced-code-blocks"])

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Gemini Code Analysis Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f9f9f9;
            font-size: 18px;
            line-height: 1.6;
        }}
        h1 {{
            font-size: 36px;
            color: #2c3e50;
            text-align: center;
        }}
        .section {{
            background-color: #ffffff;
            border-left: 8px solid #3498db;
            padding: 25px;
            margin-bottom: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }}
        pre {{
            background-color: #272822;
            color: #f8f8f2;
            padding: 15px;
            font-size: 16px;
            border-radius: 5px;
            overflow: auto;
        }}
        code {{
            font-family: Consolas, monospace;
        }}
    </style>
</head>
<body>
    <h1>🚀 Gemini Code Analysis Report</h1>

    <div class="section">
        <h2>🧮 Dataset</h2>
        <pre>{escaped_dataset}</pre>
    </div>

    <div class="section">
        <h2>📜 User Code</h2>
        <pre>{escaped_code}</pre>
    </div>

    <div class="section">
        <h2>🔍 Gemini Analysis</h2>
        {formatted_analysis}
    </div>
</body>
</html>
"""

    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    output_filename = f"gemini_analysis_{timestamp}.html"
    output_path = os.path.join(reports_dir, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n✅ Gemini analysis saved to {output_path}")

# === Main ===
if __name__ == "__main__":
    dataset, user_code = get_user_input()
    _, timestamp = save_code_to_file(user_code)
    analysis = analyze_with_gemini(user_code, dataset)
    save_html_output(user_code, dataset, analysis, timestamp)
