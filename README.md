# TestGenie - AI-Powered Unit Test Generator

![TestGenie Logo](https://via.placeholder.com/150x150?text=TestGenie)

TestGenie is an AI-powered tool that automatically generates comprehensive unit tests for your code. Using advanced language models, TestGenie analyzes your code, detects the programming language, and creates appropriate test cases using the selected testing framework.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Option 1: Using the Web Interface](#option-1-using-the-web-interface)
  - [Option 2: Running Locally](#option-2-running-locally)
  - [Option 3: GitHub Actions Integration](#option-3-github-actions-integration)
- [Usage Guide](#usage-guide)
  - [Web Interface](#web-interface)
  - [Supported Languages and Frameworks](#supported-languages-and-frameworks)
  - [Feedback-Based Refinement](#feedback-based-refinement)
- [Contributing](#contributing)

## Features

- **Automatic Language Detection**: TestGenie identifies your programming language
- **Multiple Testing Frameworks**: Support for Pytest, JUnit, and Doctest
- **Comprehensive Test Coverage**: Generates tests for normal cases, edge cases, and exceptions
- **Feedback Mechanism**: Refine generated tests based on your requirements
- **Easy Export**: Copy to clipboard or download generated tests with proper file extensions
- **GitHub Actions Integration**: Automatically generate tests for your pull requests

## Getting Started

### Option 1: Using the Web Interface

The easiest way to use TestGenie is through our hosted web interface:

1. Visit [https://testgenie.com](https://testgenie.com)
2. Paste your code in the input area
3. Select your preferred testing framework
4. Click "Generate Test Cases"

No installation required!

### Option 2: Running Locally

If you prefer to run TestGenie on your own machine:

#### Prerequisites

- Python 3.8+
- Node.js 14+
- OpenAI API key or Azure OpenAI credentials

#### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/testgenie.git
   cd testgenie
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API credentials:
   ```
   # Option 1: OpenAI API
   OPENAI_API_KEY=your_api_key_here
   
   # Option 2: Azure OpenAI
   AZURE_OPENAI_API_KEY=your_azure_api_key_here
   AZURE_OPENAI_ENDPOINT=your_azure_endpoint_here
   AZURE_OPENAI_API_VERSION=your_api_version_here
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
   ```

5. Start the Flask backend:
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```
   The application will be available at `http://localhost:3000`

### Option 3: GitHub Actions Integration

TestGenie can be integrated into your GitHub workflow to automatically generate test cases for pull requests:

1. Add the following GitHub Actions workflow file to your repository at `.github/workflows/testgenie.yml`:

```yaml
name: Auto Generate Unit Tests

on:
  pull_request  # Runs on any file change in a PR

permissions:
  contents: write  # Allows GitHub Actions to push commits

jobs:
  test-generation:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install Python dependencies
      run: |
        pip install -r requirements.txt

    - name: Start Flask backend (Azure OpenAI)
      working-directory: src  # 🔁 change if app.py is in a different folder
      env:
        AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
        AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
        AZURE_OPENAI_API_VERSION: ${{ secrets.AZURE_OPENAI_API_VERSION }}
        AZURE_OPENAI_DEPLOYMENT_NAME: ${{ secrets.AZURE_OPENAI_DEPLOYMENT_NAME }}
      run: |
        nohup python app.py & sleep 5

    - name: Run Test Generator Script
      run: |
        python test_generator.py
        echo "✅ Test cases written to generated_tests_report.md"
        echo "---- GENERATED TEST CASES ----"
        cat generated_tests_report.md || echo "⚠️ No test file generated"

    - name: Commit and push generated test cases and report
      if: success() && (hashFiles('generated_tests_report.md') != '' || hashFiles('generated_unit_test_cases/**') != '')
      run: |
        git config --global user.name "github-actions[bot]"
        git config --global user.email "github-actions[bot]@users.noreply.github.com"

        mkdir -p reports
        mv generated_tests_report.md reports/generated_tests_report.md || true

        git fetch origin ${{ github.head_ref }}
        git checkout ${{ github.head_ref }}

        git add reports/generated_tests_report.md
        git add generated_unit_test_cases/

        git diff --cached --quiet || git commit -m "🧪 Add generated unit test cases and report"

        git push origin ${{ github.head_ref }}
```

2. Add the required secrets to your GitHub repository:
   - Go to your repository settings
   - Navigate to "Secrets and variables" → "Actions"
   - Add the following secrets:
     - `AZURE_OPENAI_API_KEY`
     - `AZURE_OPENAI_ENDPOINT`
     - `AZURE_OPENAI_API_VERSION`
     - `AZURE_OPENAI_DEPLOYMENT_NAME`

3. The GitHub Action will now automatically run on any pull request, generating test cases for your code changes.

## Usage Guide

### Web Interface

The TestGenie web interface is intuitive and easy to use:

1. **Input Code**: Paste your code into the left panel
2. **Select Framework**: Choose the appropriate testing framework from the dropdown
3. **Generate Tests**: Click the "Generate Test Cases" button
4. **View Results**: Examine the generated tests in the right panel
5. **Export Tests**: Copy to clipboard or download as a file
6. **Refine Tests (Optional)**: Provide feedback to improve the generated tests

### Supported Languages and Frameworks

TestGenie currently supports:

| Language | Frameworks |
|----------|------------|
| Python   | Pytest, Doctest |
| Java     | JUnit |

Additional languages and frameworks will be added in future updates.

### Feedback-Based Refinement

If you want to improve the generated tests:

1. After generating initial tests, review them for completeness
2. Enter specific feedback in the feedback box (e.g., "Add more edge cases" or "Use mocks for the database calls")
3. Click "Submit Feedback & Regenerate"
4. TestGenie will create new tests incorporating your feedback

## Contributing

We welcome contributions to TestGenie! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to submit pull requests, report issues, and suggest enhancements.


---

© 2025 TestGenie | [testgenie.com](https://testgenie.com) | [GitHub Repository](https://github.com/yourusername/testgenie)