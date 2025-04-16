# Unit Test Generator

## Overview

Unit Test Generator (TestGenie) is an AI-powered tool that automatically creates unit tests for your code. By analyzing your source code, TestGenie detects the programming language and generates appropriate test cases using the selected testing framework.

## Features

- **Automatic Language Detection**: Identifies the programming language of your code
- **Multiple Framework Support**: Generates tests for Pytest, JUnit, and Doctest
- **Test Case Refinement**: Provides feedback mechanism to improve generated tests
- **One-Click Export**: Download tests or copy to clipboard with a single click
- **GitHub Actions Integration**: Automatically generate tests on pull requests

## Accessing the Web Interface

The Unit Test Generator is accessible online at [https://testgenie.com](https://testgenie.com)

## Using the Web Interface

### Step 1: Enter Your Code

Paste your source code into the text area on the left side of the screen.

### Step 2: Select a Testing Framework

Choose the appropriate testing framework from the dropdown menu:
- **Pytest**: For Python code using pytest framework
- **JUnit**: For Java code using JUnit framework
- **Doctest**: For Python code using doctest framework

### Step 3: Generate Test Cases

Click the "Generate Test Cases" button to analyze your code and create test cases.

### Step 4: Review and Export

The generated test cases will appear on the right side of the screen. You can:
- Copy the test cases to your clipboard using the "Copy to Clipboard" button
- Download the test cases as a file using the "Download as File" button

### Step 5: Refine the Test Cases (Optional)

If you want to improve the generated tests:
1. Enter your feedback in the text area below the test cases
2. Click "Submit Feedback & Regenerate" to create updated test cases based on your feedback

## GitHub Actions Integration

You can integrate Unit Test Generator directly into your GitHub workflow to automatically generate test cases on pull requests.

### Setup Instructions

1. Create a `.github/workflows` directory in your repository if it doesn't already exist
2. Create a new file in this directory named `test-genie.yml`
3. Copy the following workflow definition into this file:

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

4. Add the following secrets to your GitHub repository:
   - `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI service endpoint
   - `AZURE_OPENAI_API_VERSION`: The API version to use
   - `AZURE_OPENAI_DEPLOYMENT_NAME`: The deployment name for the model

### How the GitHub Action Works

1. When a pull request is created or updated, the workflow is triggered
2. The action checks out your code and sets up the required dependencies
3. It starts a temporary Flask server to handle the test generation
4. The test generator script processes changed files and generates appropriate test cases
5. Generated tests are saved in the `generated_unit_test_cases` directory
6. A report is created at `reports/generated_tests_report.md`
7. The action commits and pushes these files to your pull request branch

### Configuration Options

#### requirements.txt

Ensure your repository has a `requirements.txt` file containing:

```
flask==2.0.1
flask-cors==3.0.10
openai==1.3.0
python-dotenv==0.19.1
requests==2.26.0
```

#### Directory Structure

Make sure the following files are in the correct locations:

- `app.py`: The Flask backend application (in the `src` directory by default)
- `test_generator.py`: The script that processes files and generates tests (in the repository root)

## Supported Languages & Frameworks

| Language | Frameworks |
|----------|------------|
| Python   | Pytest, Doctest |
| Java     | JUnit |

## Best Practices

For optimal test generation:

1. **Ensure your code is well-structured**: Functions/methods with clear inputs and outputs produce better tests
2. **Include docstrings/comments**: These help the AI understand your code's intent
3. **Provide specific feedback**: When refining test cases, specify exactly what aspects need improvement
4. **Use appropriate frameworks**: Select the framework that best matches your code's language

## Troubleshooting

### Common Issues

**Error: "No code provided"**
- Make sure you've pasted code into the input area

**Error: "Language and framework mismatch"**
- Ensure you've selected the appropriate testing framework for your code's language

**GitHub Action fails to generate tests**
- Check that your repository has the correct secrets configured
- Verify the working directory in the workflow file matches your repository structure

### Getting Help

If you encounter any issues not covered here, please:
1. Check the [FAQ](https://testgenie.com/faq) on our website
2. Submit a support request through our [contact form](https://testgenie.com/contact)

## License

This project is licensed under the MIT License - see the LICENSE file for details.