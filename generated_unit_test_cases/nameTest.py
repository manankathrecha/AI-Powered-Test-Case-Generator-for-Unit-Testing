import pytest
from app import app, detect_language, generate_test_cases, extract_class_name, save_test_case_to_file

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Test detect_language function
def test_detect_language_valid_code(mocker):
    # Mock AzureOpenAI response
    mock_response = mocker.Mock()
    mock_response.choices = [mocker.Mock(message=mocker.Mock(content="Python"))]
    mocker.patch("openai.AzureOpenAI.chat.completions.create", return_value=mock_response)

    code = "def hello_world():\n    print('Hello, World!')"
    language = detect_language(code)
    assert language == "Python"  # Normal input test

def test_detect_language_invalid_code(mocker):
    # Mock AzureOpenAI response for invalid code
    mock_response = mocker.Mock()
    mock_response.choices = [mocker.Mock(message=mocker.Mock(content="Unknown"))]
    mocker.patch("openai.AzureOpenAI.chat.completions.create", return_value=mock_response)

    code = "This is not code."
    language = detect_language(code)
    assert language == "Unknown"  # Edge case test

def test_detect_language_exception_handling(mocker):
    # Mock AzureOpenAI to raise an exception
    mocker.patch("openai.AzureOpenAI.chat.completions.create", side_effect=Exception("API Error"))

    code = "def hello_world():\n    print('Hello, World!')"
    language = detect_language(code)
    assert language == "Unknown"  # Invalid input test

# Test generate_test_cases function
def test_generate_test_cases_valid_code(mocker):
    # Mock AzureOpenAI response
    mock_response = mocker.Mock()
    mock_response.choices = [mocker.Mock(message=mocker.Mock(content="def test_hello_world():\n    assert True"))]
    mocker.patch("openai.AzureOpenAI.chat.completions.create", return_value=mock_response)

    code = "def hello_world():\n    print('Hello, World!')"
    framework = "pytest"
    test_code = generate_test_cases(code, "Python", framework)
    assert "def test_hello_world()" in test_code  # Normal input test

def test_generate_test_cases_exception_handling(mocker):
    # Mock AzureOpenAI to raise an exception
    mocker.patch("openai.AzureOpenAI.chat.completions.create", side_effect=Exception("API Error"))

    code = "def hello_world():\n    print('Hello, World!')"
    framework = "pytest"
    test_code = generate_test_cases(code, "Python", framework)
    assert "# Error generating test cases" in test_code  # Invalid input test

# Test extract_class_name function
def test_extract_class_name_valid_python_code():
    code = "class HelloWorld:\n    def greet(self):\n        print('Hello, World!')"
    language = "Python"
    class_name = extract_class_name(code, language)
    assert class_name == "HelloWorld"  # Normal input test

def test_extract_class_name_no_class():
    code = "def hello_world():\n    print('Hello, World!')"
    language = "Python"
    class_name = extract_class_name(code, language)
    assert class_name == "Generated"  # Edge case test

def test_extract_class_name_valid_java_code():
    code = "public class HelloWorld {\n    public void greet() {\n        System.out.println('Hello, World!');\n    }\n}"
    language = "Java"
    class_name = extract_class_name(code, language)
    assert class_name == "HelloWorld"  # Normal input test

# Test save_test_case_to_file function
def test_save_test_case_to_file(tmp_path):
    class_name = "HelloWorld"
    language = "Python"
    test_code = "def test_hello_world():\n    assert True"
    save_test_case_to_file(class_name, language, test_code)

    file_path = tmp_path / "generated_unit_test_cases" / "HelloWorldTest.py"
    assert file_path.exists()  # Normal input test
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "def test_hello_world()" in content

# Test /generate_tests endpoint
def test_generate_tests_endpoint(client, mocker):
    # Mock detect_language and generate_test_cases
    mocker.patch("app.detect_language", return_value="Python")
    mocker.patch("app.generate_test_cases", return_value="def test_hello_world():\n    assert True")
    mocker.patch("app.extract_class_name", return_value="Hello