import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=dotenv_path)

MODEL_NAME = os.getenv("MODEL_NAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

def analyze_with_gemini(code, dataset, progress_callback=None):
    model = genai.GenerativeModel(MODEL_NAME)

    if progress_callback:
        progress_callback(10)
    time.sleep(0.2)

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

    if progress_callback:
        progress_callback(40)
    time.sleep(0.5)

    print("\n⏳ Sending code to Gemini for analysis...\n")
    response = model.generate_content(prompt)

    if progress_callback:
        progress_callback(80)
    time.sleep(0.3)

    print("\n📊 Gemini Analysis Output:\n")
    print(response.text)

    if progress_callback:
        progress_callback(100)

    return response.text
