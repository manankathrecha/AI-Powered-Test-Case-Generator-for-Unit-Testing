import pytest
from unittest.mock import patch, MagicMock
from app import app, detect_language, generate_test_cases, extract_class_name, save_test_case_to_file

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test detect_language function
@patch("app.client.chat.completions.create")
def test_detect_language(mock_create):
    # Mock successful response from Azure OpenAI
    mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Python"))])
    code_snippet = "print('Hello, World!')"
    result = detect_language(code_snippet)
    assert result == "Python"

    # Mock exception handling
    mock_create.side_effect = Exception("API Error")
    result = detect_language(code_snippet)
    assert result == "Unknown"

# Test generate_test_cases function
@patch("app.client.chat.completions.create")
@patch("app.clean_test_code")
def test_generate_test_cases(mock_clean_test_code, mock_create):
    # Mock successful response from Azure OpenAI
    mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="def test_example(): pass"))])
    mock_clean_test_code.return_value = "def test_example(): pass"
    code_snippet = "def add(a, b): return a + b"
    result = generate_test_cases(code_snippet, "Python", "pytest")
    assert result == "def test_example(): pass"

    # Mock exception handling
    mock_create.side_effect = Exception("API Error")
    result = generate_test_cases(code_snippet, "Python", "pytest")
    assert "# Error generating test cases" in result

# Test extract_class_name function
def test_extract_class_name():
    python_code = "class MyClass:\n    pass"
    java_code = "public class MyClass {\n    }"
    unknown_code = "def my_function(): pass"

    assert extract_class_name(python_code, "Python") == "MyClass"
    assert extract_class_name(java_code, "Java") == "MyClass"
    assert extract_class_name(unknown_code, "Python") == "Generated"

# Test save_test_case_to_file function
@patch("os.makedirs")
@patch("builtins.open", create=True)
def test_save_test_case_to_file(mock_open, mock_makedirs):
    class_name = "MyClass"
    language = "Python"
    test_code = "def test_example(): pass"

    save_test_case_to_file(class_name, language, test_code)

    # Check if the correct file path and content were used
    mock_makedirs.assert_called_once_with("generated_unit_test_cases", exist_ok=True)
    mock_open.assert_called_once_with("generated_unit_test_cases/MyClassTest.py", "w", encoding="utf-8")
    mock_open().write.assert_called_once_with(test_code)

# Test /generate_tests endpoint
@patch("app.detect_language")
@patch("app.generate_test_cases")
@patch("app.extract_class_name")
@patch("app.save_test_case_to_file")
def test_generate_tests_endpoint(mock_save, mock_extract, mock_generate, mock_detect, client):
    mock_detect.return_value = "Python"
    mock_generate.return_value = "def test_example(): pass"
    mock_extract.return_value = "MyClass"

    response = client.post("/generate_tests", json={"code": "def add(a, b): return a + b", "framework": "pytest"})
    assert response.status_code == 200
    assert response.json["detected_language"] == "Python"
    assert response.json["generated_tests"] == "def test_example(): pass"

    # Test missing code in request
    response = client.post("/generate_tests", json={})
    assert response.status_code == 400
    assert response.json["error"] == "No code provided"

# Test /regenerate_tests_with_feedback endpoint
@patch("app.detect_language")
@patch("app.client.chat.completions.create")
@patch("app.clean_test_code")
def test_regenerate_with_feedback_endpoint(mock_clean, mock_create, mock_detect, client):
    mock_detect.return_value = "Python"
    mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="def test_example(): pass"))])
    mock_clean.return_value = "def test_example(): pass"

    response = client.post("/regenerate_tests_with_feedback", json={
        "code": "def add(a, b): return a + b",
        "framework": "pytest",
        "feedback": "Add more edge cases"
    })
    assert response.status_code == 200
    assert response.json["generated_tests"] == "def test_example(): pass"

    # Test exception handling
    mock_create.side