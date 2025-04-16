import sys
import os
import importlib.util
import pytest
import json
from unittest.mock import patch

# ✅ Add src directory to Python path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_dir = os.path.join(base_dir, 'src')
sys.path.append(base_dir)
sys.path.append(src_dir)

# ✅ Dynamically load app.py from src/
app_path = os.path.join(src_dir, 'app.py')
spec = importlib.util.spec_from_file_location("app", app_path)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = app_module.app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# ✅ Mock functions
def mock_detect_language(code: str):
    return "python"

def mock_generate_test_cases(code: str, language: str, framework: str):
    return f"# Mock test cases for {language} using {framework}"

@patch.object(app_module, "detect_language", side_effect=mock_detect_language)
@patch.object(app_module, "generate_test_cases", side_effect=mock_generate_test_cases)
@patch.object(app_module, "save_test_case_to_file")  # prevent file writing during test
def test_generate_tests(mock_save, mock_generate, mock_detect, client):
    sample_code = "def add(a, b): return a + b"
    response = client.post("/generate_tests", json={
        "code": sample_code,
        "framework": "pytest"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["detected_language"] == "python"
    assert "# Mock test cases for python using pytest" in data["generated_tests"]

@patch.object(app_module, "detect_language", side_effect=mock_detect_language)
@patch.object(app_module.client.chat.completions, "create")
def test_regenerate_with_feedback(mock_openai, mock_detect, client):
    mock_openai.return_value.choices = [type("obj", (object,), {
        "message": type("obj", (object,), {
            "content": "# Updated test case after feedback"
        })()
    })]

    response = client.post("/regenerate_tests_with_feedback", json={
        "code": "def add(a, b): return a + b",
        "framework": "pytest",
        "feedback": "Add more edge cases"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "Updated test case" in data["generated_tests"]

def test_generate_tests_no_code(client):
    response = client.post("/generate_tests", json={"framework": "pytest"})
    assert response.status_code == 400
    assert "error" in response.get_json()