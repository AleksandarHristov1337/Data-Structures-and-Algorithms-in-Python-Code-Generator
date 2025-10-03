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
