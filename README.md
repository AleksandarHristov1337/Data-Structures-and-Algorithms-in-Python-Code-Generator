

# Data Structures and Algorithms Code Generator with Gemini AI

This project leverages **Google Gemini AI** to analyze user-submitted Python code and datasets,
focusing on data structures performance and complexity.
It generates detailed HTML reports with explanations about data structure efficiency,
Big-O notations, and suggestions for algorithm improvements.

---

## Features

- Accepts user input for datasets and Python code via command line.
- Uses Google Gemini AI to analyze:
  - Fastest, average, and slowest data structures based on algorithmic complexity.
  - Detailed explanations of time and space complexities.
  - Suggestions for improved algorithms.
- Saves analysis results along with code and dataset in an easy-to-read HTML report.
- Supports error handling for incorrect or broken code submissions.
- Environment configuration using `.env` file for API keys and model settings.

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/AleksandarHristov1337/Data-Structures-and-Algorithms-in-Python---Code-Generator.git
   cd src


2. Install required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root (one level above the `src` folder) with:

   ```
   GOOGLE_API_KEY=your_google_api_key_here
   MODEL_NAME=gemini-2.0-flash-001
   ```

---

## Usage

1. Run the main script from the project root or the `src` folder:

   ```bash
   python src/main.py
   ```

2. Follow the command line prompts:

   * Enter your dataset (e.g., `[5, 1, 2, 9, 5, 2, 3, 1, 8, 7]`)
   * Enter your Python code snippet to analyze.

3. The tool will generate an HTML report saved in the project directory, containing:

   * The dataset you input.
   * The code you submitted.
   * Gemini AI’s analysis and explanations.

---

## Project Structure

```
your-repo/
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point (minimal logic)
│   ├── web_app.py               # Flask app for UI
│   ├── input_handler.py         # Handles user input
│   ├── file_saver.py            # Handles saving code and HTML to reports
│   ├── gemini_analyzer.py       # Interacts with Gemini API
│   ├── html_generator.py        # Builds the HTML report
├── reports/                     # Generated reports (.txt + .html)
├── templates/
│   └── index.html           # HTML template for UI
├── static/                   # (optional) CSS, JS, etc.
├── .env                         # Contains API keys
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Requirements

* `genai`
* `python-dotenv`
* `flask`
* `markdown2`

## Troubleshooting

* If `MODEL_NAME` or `GOOGLE_API_KEY` print as `None`, confirm the `.env` file is correctly named and placed.
* Make sure to run `load_dotenv()` before accessing environment variables.
* If encountering errors submitting broken code, the tool will display error messages returned by Gemini AI in the report.

---

## License

MIT License

---

## Acknowledgments

* Powered by [Google Gemini AI](https://developers.generativeai.google/)
