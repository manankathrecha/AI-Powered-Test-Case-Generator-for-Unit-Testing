import sys
import os
import importlib.util
import pytest
from unittest.mock import patch, mock_open

# ✅ Add project root to sys.path so we can import test_generator.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Dynamically load test_generator.py
generator_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_generator.py'))
spec = importlib.util.spec_from_file_location("test_generator", generator_path)
test_generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_generator)

# ✅ Tests

@patch("test_generator.subprocess.check_output")
def test_get_changed_files_from_diff(mock_subproc):
    mock_subproc.return_value = b"example.py\nhelper.java"
    files = test_generator.get_changed_files()
    assert "example.py" in files
    assert "helper.java" in files

@patch("builtins.open", new_callable=mock_open, read_data="class Sample:\n    pass")
def test_read_file_content(mock_file):
    content = test_generator.read_file_content("dummy.py")
    assert "class Sample" in content

@patch("test_generator.requests.post")
def test_send_to_backend(mock_post):
    mock_post.return_value.json.return_value = {
        "detected_language": "python",
        "generated_tests": "def test_example(): pass"
    }
    response = test_generator.send_to_backend("code", "pytest")
    assert response["detected_language"] == "python"
    assert "generated_tests" in response

def test_extract_class_name_python():
    code = "class MyClass:\n    def method(self): pass"
    assert test_generator.extract_class_name(code, "python") == "MyClass"

def test_extract_class_name_java():
    code = "public class HelloWorld {}"
    assert test_generator.extract_class_name(code, "java") == "HelloWorld"

def test_extract_class_name_fallback():
    assert test_generator.extract_class_name("print('hello')", "python", "hello.py") == "hello"

@patch("test_generator.get_changed_files", return_value=["valid_script.py"])
@patch("test_generator.read_file_content", return_value="class AutoGen:\n    pass")
@patch("test_generator.send_to_backend", return_value={
    "detected_language": "python",
    "generated_tests": "def test_auto(): pass"
})
@patch("test_generator.open", new_callable=mock_open)
@patch("test_generator.os.makedirs")
def test_main_flow(mock_makedirs, mock_open_fn, mock_send, mock_read, mock_get_files):
    test_generator.main()
    mock_makedirs.assert_called_once()
    handle = mock_open_fn()
    handle.write.assert_any_call("def test_auto(): pass")
