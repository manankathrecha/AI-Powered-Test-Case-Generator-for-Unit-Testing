
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Detect programming language
def detect_language(code: str):
    prompt = f"""
    Analyze the following code snippet and accurately identify the programming language.

    Code:
    {code}

    Only respond with the language name, no extra text.
    """
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Language detection error:", e)
        return "Unknown"

# Generate test cases
def generate_test_cases(code: str, language: str, framework: str):
    framework_notes = {
        "pytest": "- Use `pytest` syntax, no unittest.\n- Use `assert` statements.",
        "doctest": "- Use Python docstring doctest format for inline testing.",
        "junit": "- Use JUnit 5 annotations like `@Test`, and assertions like `assertEquals`, etc."
    }

    additional_notes = "- Cover normal, edge, and invalid inputs.\n- Include comments for each test.\n- Return clean test code only."

    prompt = f"""
You are a professional {language} developer and expert in unit testing.

Write unit tests for the following code using {framework}.

Code to Test:
```{language}
{code}
```

Testing Instructions:
{framework_notes.get(framework.lower(), '')}

{additional_notes}

Output ONLY the test code — no markdown, no explanations, no extra text.
"""

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Test generation error:", e)
        return f"# Error generating test cases: {str(e)}"

# API endpoint
@app.route("/generate_tests", methods=["POST"])
def generate_tests():
    try:
        data = request.get_json()
        input_code = data.get("code")
        framework = data.get("framework", "pytest")

        if not input_code:
            return jsonify({"error": "No code provided"}), 400

        language = detect_language(input_code)
        test_code = generate_test_cases(input_code, language, framework)

        return jsonify({
            "detected_language": language,
            "generated_tests": test_code
        })
    except Exception as e:
        print("Server error:", e)
        return jsonify({"error": str(e)}), 500

# Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)