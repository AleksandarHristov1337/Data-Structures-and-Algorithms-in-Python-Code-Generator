import os
import html
import markdown2

def generate_html(code, dataset, analysis):
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
    <div class="section"><h2>🧮 Dataset</h2><pre>{escaped_dataset}</pre></div>
    <div class="section"><h2>📜 User Code</h2><pre>{escaped_code}</pre></div>
    <div class="section"><h2>🔍 Gemini Analysis</h2>{formatted_analysis}</div>
</body>
</html>"""
    return html_content
