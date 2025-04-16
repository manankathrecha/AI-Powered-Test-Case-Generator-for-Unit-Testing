import sys
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_dir = os.path.join(base_dir, 'src')
sys.path.append(src_dir)

from code_cleaning_util import clean_test_code
import pytest

def test_removes_python_markdown_block():
    code = """```python
def add(a, b):
    return a + b
```"""
    expected = """def add(a, b):
    return a + b"""
    assert clean_test_code(code) == expected

def test_removes_plain_markdown_block():
    code = """```
print("Hello World")
```"""
    expected = 'print("Hello World")'
    assert clean_test_code(code) == expected

def test_handles_no_markdown():
    code = "def multiply(a, b): return a * b"
    assert clean_test_code(code) == code

def test_strips_leading_and_trailing_whitespace():
    code = """   ```python
def subtract(a, b):
    return a - b
```   """
    expected = """def subtract(a, b):
    return a - b"""
    assert clean_test_code(code) == expected
