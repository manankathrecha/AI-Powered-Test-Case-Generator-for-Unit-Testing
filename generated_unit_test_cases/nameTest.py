import pytest
from unittest.mock import patch, MagicMock
from app import app, detect_language, generate_test_cases, extract_class_name, save_test_case_to_file

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test for detect_language function
@patch('app.client.chat.completions.create')
def test_detect_language(mock_create):
    # Mocking the Azure OpenAI response
    mock_create.return_value.choices = [MagicMock(message=MagicMock(content="Python"))]
    
    code = "print('Hello, World!')"
    language = detect_language(code)
    
    assert language == "Python"  # Normal input
    mock_create.assert_called_once()

@patch('app.client.chat.completions.create')
def test_detect_language_error(mock_create):
    # Simulate an exception in the Azure OpenAI client
    mock_create.side_effect = Exception("API Error")
    
    code = "print('Hello, World!')"
    language = detect_language(code)
    
    assert language == "Unknown"  # Error handling

# Test for generate_test_cases function
@patch('app.client.chat.completions.create')
@patch('app.clean_test_code')
def test_generate_test_cases(mock_clean_test_code, mock_create):
    # Mocking the Azure OpenAI response
    mock_create.return_value.choices = [MagicMock(message=MagicMock(content="def test_sample(): pass"))]
    mock_clean_test_code.return_value = "def test_sample(): pass"
    
    code = "def add(a, b): return a + b"
    framework = "pytest"
    test_code = generate_test_cases(code, "Python", framework)
    
    assert test_code == "def test_sample(): pass"  # Normal input
    mock_create.assert_called_once()
    mock_clean_test_code.assert_called_once()

@patch('app.client.chat.completions.create')
def test_generate_test_cases_error(mock_create):
    # Simulate an exception in the Azure OpenAI client
    mock_create.side_effect = Exception("API Error")
    
    code = "def add(a, b): return a + b"
    framework = "pytest"
    test_code = generate_test_cases(code, "Python", framework)
    
    assert "Error generating test cases" in test_code  # Error handling

# Test for extract_class_name function
def test_extract_class_name_python():
    code = "class MyClass:\n    pass"
    language = "Python"
    class_name = extract_class_name(code, language)
    
    assert class_name == "MyClass"  # Normal input

def test_extract_class_name_no_class():
    code = "def my_function(): pass"
    language = "Python"
    class_name = extract_class_name(code, language)
    
    assert class_name == "Generated"  # No class in code

# Test for save_test_case_to_file function
@patch('os.makedirs')
@patch('builtins.open')
def test_save_test_case_to_file(mock_open, mock_makedirs):
    class_name = "MyClass"
    language = "Python"
    test_code = "def test_sample(): pass"
    
    save_test_case_to_file(class_name, language, test_code)
    
    mock_makedirs.assert_called_once_with("generated_unit_test_cases", exist_ok=True)
    mock_open.assert_called_once_with("generated_unit_test_cases/MyClassTest.py", "w", encoding="utf-8")
    mock_open.return_value.write.assert_called_once_with(test_code)

# Test for /generate_tests endpoint
@patch('app.detect_language', return_value="Python")
@patch('app.generate_test_cases', return_value="def test_sample(): pass")
@patch('app.extract_class_name', return_value="MyClass")
@patch('app.save_test_case_to_file')
def test_generate_tests_endpoint(mock_save, mock_extract, mock_generate, mock_detect, client):
    response = client.post('/generate_tests', json={
        "code": "def add(a, b): return a + b",
        "framework": "pytest"
    })
    
    assert response.status_code == 200  # Normal input
    assert response.json['detected_language'] == "Python"
    assert response.json['generated_tests'] == "def test_sample(): pass"
    mock_detect.assert_called_once()
    mock_generate.assert_called_once()
    mock_extract.assert_called_once()
    mock_save.assert_called_once()

def test_generate_tests_endpoint_no_code(client):
    response = client.post('/generate_tests', json={})
    
    assert response.status_code == 400  # Missing code
    assert response.json['error'] == "No code provided"

# Test for /regenerate_tests_with_feedback endpoint
@patch('app.detect_language', return_value="Python")
@patch