```python
import pytest
from unittest.mock import patch, mock_open
import subprocess
import requests

@pytest.fixture
def mock_subprocess_check_output():
    with patch("subprocess.check_output") as mock:
        yield mock

@pytest.fixture
def mock_requests_post():
    with patch("requests.post") as mock:
        yield mock

def test_get_changed_files_normal_case(mock_subprocess_check_output):
    mock_subprocess_check_output.return_value = b"file1.py\nfile2.java\n"
    result = get_changed_files()
    assert result == ["file1.py", "file2.java"]

def test_get_changed_files_fallback_case(mock_subprocess_check_output):
    mock_subprocess_check_output.side_effect = [subprocess.CalledProcessError(1, "git diff"), b"file1.py\nfile2.java\n"]
    result = get_changed_files()
    assert result == ["file1.py", "file2.java"]

def test_get_changed_files_error_case(mock_subprocess_check_output):
    mock_subprocess_check_output.side_effect = Exception("Unexpected error")
    result = get_changed_files()
    assert result == []

def test_read_file_content_success():
    mock_data = "class Test:\n    pass"
    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = read_file_content("file1.py")
    assert result == mock_data

def test_read_file_content_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
        result = read_file_content("nonexistent.py")
    assert result == ""

def test_read_file_content_permission_error():
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        result = read_file_content("restricted.py")
    assert result == ""

def test_send_to_backend_success(mock_requests_post):
    mock_requests_post.return_value.json.return_value = {"detected_language": "Python", "generated_tests": "test_code"}
    result = send_to_backend("class Test:\n    pass", "pytest")
    assert result == {"detected_language": "Python", "generated_tests": "test_code"}

def test_send_to_backend_api_error(mock_requests_post):
    mock_requests_post.side_effect = requests.exceptions.RequestException("API error")
    result = send_to_backend("class Test:\n    pass", "pytest")
    assert result == {"error": "API error: API error"}

def test_extract_class_name_python():
    code = "class MyClass:\n    pass"
    result = extract_class_name(code, "Python")
    assert result == "MyClass"

def test_extract_class_name_java():
    code = "public class MyJavaClass {\n    // code here\n}"
    result = extract_class_name(code, "Java")
    assert result == "MyJavaClass"

def test_extract_class_name_no_class():
    code = "def my_function():\n    pass"
    result = extract_class_name(code, "Python")
    assert result == "Generated"
```