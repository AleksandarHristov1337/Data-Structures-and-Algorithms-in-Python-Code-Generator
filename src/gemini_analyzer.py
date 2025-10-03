import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=dotenv_path)

MODEL_NAME = os.getenv("MODEL_NAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

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
