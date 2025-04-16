```python
import pytest
from unittest.mock import patch, mock_open, MagicMock
import os
import subprocess
import requests
from main import (
    get_changed_files,
    read_file_content,
    send_to_backend,
    extract_class_name,
    SUPPORTED_EXTENSIONS,
    FRAMEWORK_MAP,
)

# Test get_changed_files
@patch("subprocess.check_output")
def test_get_changed_files_normal_case(mock_check_output):
    # Mock git diff output
    mock_check_output.return_value = b"file1.py\nfile2.java\n"
    result = get_changed_files()
    assert result == ["file1.py", "file2.java"]

@patch("subprocess.check_output")
def test_get_changed_files_fallback_case(mock_check_output):
    # Simulate HEAD~1 failure and fallback to git ls-files
    mock_check_output.side_effect = [subprocess.CalledProcessError(1, "git diff"), b"file1.py\nfile2.java\n"]
    result = get_changed_files()
    assert result == ["file1.py", "file2.java"]

@patch("subprocess.check_output")
def test_get_changed_files_error(mock_check_output):
    # Simulate an error in subprocess
    mock_check_output.side_effect = Exception("Error")
    result = get_changed_files()
    assert result == []

# Test read_file_content
@patch("builtins.open", new_callable=mock_open, read_data="print('Hello, World!')")
def test_read_file_content_success(mock_file):
    result = read_file_content("test.py")
    assert result == "print('Hello, World!')"

@patch("builtins.open", side_effect=Exception("File not found"))
def test_read_file_content_error(mock_file):
    result = read_file_content("nonexistent.py")
    assert result == ""

# Test send_to_backend
@patch("requests.post")
def test_send_to_backend_success(mock_post):
    mock_post.return_value.json.return_value = {"detected_language": "python", "generated_tests": "test_code"}
    result = send_to_backend("code", "pytest")
    assert result == {"detected_language": "python", "generated_tests": "test_code"}

@patch("requests.post", side_effect=Exception("API error"))
def test_send_to_backend_error(mock_post):
    result = send_to_backend("code", "pytest")
    assert result == {"error": "API error: API error"}

# Test extract_class_name
def test_extract_class_name_python():
    code = "class MyClass:\n    pass"
    result = extract_class_name(code, "python")
    assert result == "MyClass"

def test_extract_class_name_java():
    code = "public class MyClass {\n}"
    result = extract_class_name(code, "java")
    assert result == "MyClass"

def test_extract_class_name_no_class():
    code = "def my_function():\n    pass"
    result = extract_class_name(code, "python")
    assert result == "Generated"

# Test main logic helpers
def test_supported_extensions():
    assert ".py" in SUPPORTED_EXTENSIONS
    assert ".java" in SUPPORTED_EXTENSIONS

def test_framework_map():
    assert FRAMEWORK_MAP[".py"] == "pytest"
    assert FRAMEWORK_MAP[".java"] == "JUnit"
```