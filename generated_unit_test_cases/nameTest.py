```python
import pytest
from flask import Flask
from flask.testing import FlaskClient
import json
from unittest.mock import patch

# Test setup
@pytest.fixture
def client():
    app = Flask(__name__)
    app.testing = True
    with app.test_client() as client:
        yield client

# Test: Detect Language Endpoint
@patch("openai.AzureOpenAI.chat.completions.create")
def test_detect_language(mock_openai, client):
    # Mock OpenAI response
    mock_openai.return_value = type("obj", (object,), {
        "choices": [{"message": {"content": "Python"}}]
    })
    
    response = client.post("/generate_tests", data=json.dumps({
        "code": "print('Hello, World!')",
        "framework": "pytest"
    }), content_type="application/json")
    
    assert response.status_code == 200
    assert response.json["detected_language"] == "Python"
    assert "generated_tests" in response.json

# Test: Generate Tests Endpoint - Missing Code
def test_generate_tests_missing_code(client):
    response = client.post("/generate_tests", data=json.dumps({
        "framework": "pytest"
    }), content_type="application/json")
    
    assert response.status_code == 400
    assert response.json["error"] == "No code provided"

# Test: Generate Tests Endpoint - Invalid Framework
@patch("openai.AzureOpenAI.chat.completions.create")
def test_generate_tests_invalid_framework(mock_openai, client):
    # Mock OpenAI response
    mock_openai.return_value = type("obj", (object,), {
        "choices": [{"message": {"content": "Python"}}]
    })
    
    response = client.post("/generate_tests", data=json.dumps({
        "code": "print('Hello, World!')",
        "framework": "unknown_framework"
    }), content_type="application/json")
    
    assert response.status_code == 200
    assert response.json["detected_language"] == "Python"
    assert "generated_tests" in response.json

# Test: Regenerate Tests with Feedback Endpoint
@patch("openai.AzureOpenAI.chat.completions.create")
def test_regenerate_tests_with_feedback(mock_openai, client):
    # Mock OpenAI response
    mock_openai.return_value = type("obj", (object,), {
        "choices": [{"message": {"content": "def test_example(): pass"}]}
    })
    
    response = client.post("/regenerate_tests_with_feedback", data=json.dumps({
        "code": "print('Hello, World!')",
        "framework": "pytest",
        "feedback": "Add more edge cases"
    }), content_type="application/json")
    
    assert response.status_code == 200
    assert "generated_tests" in response.json

# Test: Regenerate Tests with Feedback Endpoint - Missing Code
def test_regenerate_tests_with_feedback_missing_code(client):
    response = client.post("/regenerate_tests_with_feedback", data=json.dumps({
        "framework": "pytest",
        "feedback": "Add more edge cases"
    }), content_type="application/json")
    
    assert response.status_code == 500
    assert "error" in response.json

# Test: Extract Class Name
def test_extract_class_name_python():
    from app import extract_class_name
    code = "class MyClass:\n    pass"
    language = "Python"
    assert extract_class_name(code, language) == "MyClass"

def test_extract_class_name_java():
    from app import extract_class_name
    code = "public class MyClass {\n    // code\n}"
    language = "Java"
    assert extract_class_name(code, language) == "MyClass"

def test_extract_class_name_no_class():
    from app import extract_class_name
    code = "def my_function(): pass"
    language = "Python"
    assert extract_class_name(code, language) == "Generated"

# Test: Save Test Case to File
def test_save_test_case_to_file(tmp_path):
    from app import save_test_case_to_file
    class_name = "MyClass"
    language = "Python"
    test_code = "def test_example(): pass"
    
    save_test_case_to_file(class_name, language, test_code)
    file_path = tmp_path / "generated_unit_test_cases" / "MyClassTest.py"
    
    assert file_path.exists()
    with open(file_path, "r") as f:
        content = f.read()
    assert content == test_code
```