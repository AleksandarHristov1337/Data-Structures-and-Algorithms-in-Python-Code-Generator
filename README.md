# WORK IN PROGRESS - THIS README DOESN'T REFLECT ALL CHANGES MADE AT THIS MOMENT OF DEVELOPMENT

# ⚙️ Data Structures and Algorithms Code Generator with Gemini AI

This project leverages **Google Gemini AI** to analyze user-submitted Python code and datasets — focusing on data structure performance and algorithm complexity. It generates detailed HTML reports with:

- Efficiency breakdowns (fastest, average, slowest)
- Big-O notations
- Space/time complexity explanations
- Suggestions for algorithmic improvements


## 🚀 Features

- Accepts input via **command line** or **web UI**
- Uses Google Gemini AI to analyze:
  - Fastest, average, and slowest data structures
  - Time and space complexity details
  - Optimized algorithm suggestions
- Generates rich **HTML reports**
- Execute DSA Code And Report Performance On Graph
- Built-in error handling for code issues
- Modular structure for easy development
- Uses `.env` for secure API key configuration

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AleksandarHristov1337/Data-Structures-and-Algorithms-in-Python---Code-Generator.git
cd Data-Structures-and-Algorithms-in-Python---Code-Generator
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Your API Key

Create a `.env` file at the **project root** (above `src/`) and add:

```env
GOOGLE_API_KEY=your_google_api_key_here
MODEL_NAME=gemini-2.0-flash-001
```

---

## 🧠 Usage Options

### ➤ Option 1: Command Line Interface (CLI)

Run the main script:

```bash
python src/main.py
```

Follow prompts to input your dataset and Python code. Once complete, a report will be saved in the `reports/` directory.

---

### ➤ Option 2: Web User Interface (UI)

1. Run the Flask app:

   ```bash
   python src/web_app.py
   ```

2. Open your browser and visit:
   [http://localhost:5000](http://localhost:5000)

3. Input your dataset and code. A spinner will indicate loading. You’ll be redirected to a page with a link to your generated report.

---

## 📁 Project Structure

```
your-repo/
├── src/
│   ├── __init__.py
│   ├── main.py                # CLI entry point
│   ├── web_app.py             # Flask app for UI
│   ├── input_handler.py       # Handles user input
│   ├── file_saver.py          # Saves user code & HTML reports
│   ├── gemini_analyzer.py     # Communicates with Gemini API
│   ├── html_generator.py      # Builds the HTML report
├── templates/
│   └── index.html             # UI form
│   └── result.html            # Report generated confirmation
│   └── execute.html           # Execute DSA Code And Report Performance On Graph
├── static/                    # Optional CSS/JS if needed
├── reports/                   # Output: user_code_*.txt & gemini_analysis_*.html
├── .env                       # API key config
├── requirements.txt           # Python dependencies
└── README.md                  # This file 
```

---

## ✅ Requirements

```txt
google-generativeai
python-dotenv
flask
markdown2
```

To regenerate `requirements.txt` after installing packages:

```bash
pip freeze > requirements.txt
```

---
## Future Plans

* 🧠 **Planned** Make it be able to be ran by more AI(LLM) providers others than Google Gemini AI.

## 🧩 Troubleshooting

* ✅ **API Keys Missing?** Make sure `.env` is placed **in the root**, not in `src/`.
* ✅ **Environment Not Loading?** Ensure `load_dotenv()` is called in relevant files.
* ⚠️ **Broken Code Submitted?** Gemini will attempt to analyze and return helpful errors.
* 🖥️ **Spinner Not Showing in UI?** Ensure JavaScript isn't blocked in your browser.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🙏 Acknowledgments

* Powered by [🌟 Google Gemini AI](https://developers.generativeai.google/)
---

## EXAMPLE ENV 
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.0-flash-001
FLASK_SECRET_KEY=supersecretkey
DATABASE_URL=postgresql+psycopg2://postgres:yourpassword@localhost/yourdbname
SUPERUSER_PASSWORD=not_used_right_now
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secureadminpass
