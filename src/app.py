from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend communication
CORS(app, resources={r"/*": {"origins": "*"}})

# OpenAI API key setup (HARD-CODED as before)
client = OpenAI(api_key="*")  # 🔴 Replace with your actual API key

# Function to detect the programming language
def detect_language(code: str):
    prompt = f"""
    Analyze the following code snippet and accurately identify the programming language.
    
    Code:
    {code}
    
    Only respond with the language name, without any additional text.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Unknown"

# Function to generate unit tests based on detected language
def generate_test_cases(code: str, language: str):
    prompt = f"""
    You are a highly skilled software engineer specializing in {language}.  
    Your task is to generate **comprehensive, well-structured unit tests** for the given code.  

    ### **Code to test:**
    ```{language}
    {code}
    ```

    ### **Instructions:**
    - **Follow best practices** for unit testing in {language}.
    - Use the **appropriate testing framework** for {language}.
    - Cover **all possible scenarios**, including:
      - ✅ **Standard cases** (normal input values)
      - 🛑 **Edge cases** (boundary values, extreme inputs)
      - ❌ **Invalid cases** (handling errors & exceptions)
    - If the function interacts with **external dependencies**, use **mocks/stubs**.
    - Ensure tests are **clear, maintainable, and efficient**.
    - **Include comments** explaining each test case.

    ### **Expected Output:**
    - A complete, runnable test suite.
    - Uses proper assertions and structure.
    - No unnecessary or redundant test cases.

    **Generated Unit Tests:**
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,  # Lowered for more deterministic responses
            max_tokens=600  # Increased for more detailed test cases
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating test cases: {str(e)}"

@app.route("/generate_tests", methods=["POST"])
def generate_tests():
    try:
        data = request.get_json()
        input_code = data.get("code")

        if not input_code:
            return jsonify({"error": "No code provided"}), 400

        # Detect language
        detected_language = detect_language(input_code)

        # Generate test cases
        test_cases = generate_test_cases(input_code, detected_language)

        return jsonify({
            "detected_language": detected_language,
            "generated_tests": test_cases
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
