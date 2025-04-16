import pytest
from unittest.mock import patch, mock_open
import subprocess
import requests

# Test get_changed_files
@patch("subprocess.check_output")
def test_get_changed_files_head_diff(mock_check_output):
    mock_check_output.return_value = b"file1.py\nfile2.java\n"
    result = get_changed_files()
    assert result == ["file1.py", "file2.java"]

@patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "git"))
def test_get_changed_files_fallback(mock_check_output):
    mock_check_output.side_effect = [subprocess.CalledProcessError(1, "git"), b"file3.py\nfile4.java\n"]
    result = get_changed_files()
    assert result == ["file3.py", "file4.java"]

@patch("subprocess.check_output", side_effect=Exception("Error"))
def test_get_changed_files_error(mock_check_output):
    result = get_changed_files()
    assert result == []

# Test read_file_content
@patch("builtins.open", new_callable=mock_open, read_data="print('Hello World')")
def test_read_file_content_valid(mock_open_file):
    result = read_file_content("test.py")
    assert result == "print('Hello World')"

@patch("builtins.open", side_effect=Exception("File not found"))
def test_read_file_content_invalid(mock_open_file):
    result = read_file_content("missing.py")
    assert result == ""

# Test send_to_backend
@patch("requests.post")
def test_send_to_backend_success(mock_post):
    mock_post.return_value.json.return_value = {"generated_tests": "test_code", "detected_language": "python"}
    result = send_to_backend("print('Hello')", "pytest")
    assert result == {"generated_tests": "test_code", "detected_language": "python"}

@patch("requests.post", side_effect=Exception("API error"))
def test_send_to_backend_error(mock_post):
    result = send_to_backend("print('Hello')", "pytest")
    assert result == {"error": "API error: API error"}

# Test extract_class_name
def test_extract_class_name_python():
    code = "class MyClass:\n    pass"
    result = extract_class_name(code, "python")
    assert result == "MyClass"

def test_extract_class_name_java():
    code = "public class MyJavaClass {\n    public static void main(String[] args) {}"
    result = extract_class_name(code, "java")
    assert result == "MyJavaClass"

def test_extract_class_name_no_match_with_fallback():
    code = "def my_function():\n    pass"
    result = extract_class_name(code, "python", "fallback.py")
    assert result == "fallback"

def test_extract_class_name_no_match_no_fallback():
    code = "def my_function():\n    pass"
    result = extract_class_name(code, "python")
    assert result == "Generated"