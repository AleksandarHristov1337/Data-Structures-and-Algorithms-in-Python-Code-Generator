from input_handler import get_user_input
from file_saver import save_code_to_file, save_html_output
from gemini_analyzer import analyze_with_gemini

def main():
    dataset, user_code = get_user_input()
    _, timestamp = save_code_to_file(user_code)
    analysis = analyze_with_gemini(user_code, dataset)
    save_html_output(user_code, dataset, analysis, timestamp)

if __name__ == "__main__":
    main()
