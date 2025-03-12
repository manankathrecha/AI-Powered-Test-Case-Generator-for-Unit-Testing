from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend communication
CORS(app, resources={r"/*": {"origins": "*"}})

# OpenAI API key setup
client = OpenAI(api_key="*")  # Store securely in environment variables, Replace * with your API key

# Function to detect the programming language
def detect_language(code: str):
    prompt = f"""
    Identify the programming language of the following code snippet:
    
    Code:
    {code}
    
    Respond only with the language name.
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
    Given the following {language} code, generate comprehensive unit test cases
    using the appropriate testing framework for the language.
    
    Code:
    {code}
    
    Generated Unit Tests:
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
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
