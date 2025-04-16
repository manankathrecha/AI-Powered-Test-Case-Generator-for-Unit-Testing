import pytest
from code_cleaning_util import clean_test_code

# Test normal case: Removes Python markdown block
def test_removes_python_markdown_block():
    code = """```python
def add(a, b):
    return a + b
```"""
    expected = """def add(a, b):
    return a + b"""
    assert clean_test_code(code) == expected

# Test normal case: Removes plain markdown block
def test_removes_plain_markdown_block():
    code = """```
print("Hello World")
```"""
    expected = 'print("Hello World")'
    assert clean_test_code(code) == expected

# Test edge case: Handles code without markdown blocks
def test_handles_no_markdown():
    code = "def multiply(a, b): return a * b"
    assert clean_test_code(code) == code

# Test edge case: Strips leading and trailing whitespace around markdown block
def test_strips_leading_and_trailing_whitespace():
    code = """   ```python
def subtract(a, b):
    return a - b
```   """
    expected = """def subtract(a, b):
    return a - b"""
    assert clean_test_code(code) == expected

# Test edge case: Empty input string
def test_empty_input():
    code = ""
    expected = ""
    assert clean_test_code(code) == expected

# Test invalid input: Non-string input
def test_non_string_input():
    code = 12345
    with pytest.raises(TypeError):
        clean_test_code(code)

# Test edge case: Markdown block with no content
def test_empty_markdown_block():
    code = """```python
```"""
    expected = ""
    assert clean_test_code(code) == expected

# Test edge case: Multiple markdown blocks in the input
def test_multiple_markdown_blocks():
    code = """```python
def add(a, b):
    return a + b
```

```python
def subtract(a, b):
    return a - b
```"""
    expected = """def add(a, b):
    return a + b

def subtract(a, b):
    return a - b"""
    assert clean_test_code(code) == expected

# Test edge case: Mixed markdown and non-markdown content
def test_mixed_content():
    code = """Some text before
```python
def add(a, b):
    return a + b
```
Some text after"""
    expected = """Some text before
def add(a, b):
    return a + b
Some text after"""
    assert clean_test_code(code) == expected