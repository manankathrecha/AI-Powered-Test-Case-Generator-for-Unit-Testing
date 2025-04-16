import re

def clean_test_code(code: str) -> str:

# Remove leading/trailing markdown code block indicators like ```python or ```
    return re.sub(r'^```.*?\n|\n?```$', '', code.strip(), flags=re.DOTALL)