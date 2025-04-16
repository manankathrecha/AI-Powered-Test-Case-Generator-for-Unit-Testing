```python
import pytest
import json
from app import app, detect_language, generate_test_cases

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_detect_language():
    # Test Python code detection
    code = 'print("Hello, World!")'
    result = detect_language(code)
    assert result == 'Python'

    # Test JavaScript code detection
    code = 'console.log("Hello, World!");'
    result = detect_language(code)
    assert result == 'JavaScript'

    # Test unknown language detection
    code = 'unknown language code'
    result = detect_language(code)
    assert result == 'Unknown'

def test_generate_test_cases():
    # Test Python test case generation
    code = 'def add(a, b): return a + b'
    language = 'Python'
    result = generate_test_cases(code, language)
    assert result is not None

    # Test JavaScript test case generation
    code = 'function add(a, b) { return a + b; }'
    language = 'JavaScript'
    result = generate_test_cases(code, language)
    assert result is not None

    # Test invalid language input
    code = 'print("Hello, World!")'
    language = 'Unknown'
    result = generate_test_cases(code, language)
    assert result is None

def test_generate_tests_endpoint(client):
    # Test valid request with Python code
    response = client.post('/generate_tests', data=json.dumps({"code": 'print("Hello, World!")'}), content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.get_data())
    assert data["detected_language"] == 'Python'
    assert data["generated_tests"] is not None

    # Test valid request with JavaScript code
    response = client.post('/generate_tests', data=json.dumps({"code": 'console.log("Hello, World!");'}), content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.get_data())
    assert data["detected_language"] == 'JavaScript'
    assert data["generated_tests"] is not None

    # Test invalid request with empty payload
    response = client.post('/generate_tests', data=json.dumps({}), content_type='application/json')
    assert response.status_code == 400

    # Test invalid request with missing 'code' field
    response = client.post('/generate_tests', data=json.dumps({"language": "Python"}), content_type='application/json')
    assert response.status_code == 400
```