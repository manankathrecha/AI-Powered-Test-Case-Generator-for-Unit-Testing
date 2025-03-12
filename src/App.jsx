import React, { useState, useCallback } from "react";
import './App.css';

function App() {
  const [inputCode, setInputCode] = useState('');
  const [detectedLanguage, setDetectedLanguage] = useState('');
  const [generatedTestCases, setGeneratedTestCases] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerateClick = useCallback(async () => {
    if (!inputCode.trim()) {
      setError("Please enter some code to analyze.");
      return;
    }

    setLoading(true);
    setError(''); // Clear previous errors

    try {
      const response = await fetch("http://127.0.0.1:5000/generate_tests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code: inputCode }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate test cases: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.detected_language && data.generated_tests) {
        setDetectedLanguage(data.detected_language);
        setGeneratedTestCases(data.generated_tests);
      } else {
        setDetectedLanguage("Could not detect language.");
        setGeneratedTestCases("No test cases generated.");
      }

    } catch (error) {
      console.error("Error:", error);
      setError("An error occurred. Please try again later.");
      setDetectedLanguage("Error: " + error.message);
      setGeneratedTestCases("Error: " + error.message);
    } finally {
      setLoading(false);
    }
  }, [inputCode]);

  return (
    <div className="App">
      <div className="left-side">
        <h1>Unit Test Case Generator</h1>
        <p className="subtitle">Paste your code below to automatically generate unit test cases.</p>

        <textarea
          placeholder="Paste your code here..."
          value={inputCode}
          onChange={(e) => setInputCode(e.target.value)}
          rows="10"
        ></textarea>

        <button onClick={handleGenerateClick} disabled={loading} className={loading ? "analyze-button loading" : "analyze-button"}>
          {loading ? <div className="spinner"></div> : "Generate Test Cases"}
        </button>

        {error && <p className="error">{error}</p>}

        <div className="detected-smell">
          <h2>Detected Language</h2>
          <div className="output-content">
            {detectedLanguage || "Language will be detected when you generate test cases."}
          </div>
        </div>
      </div>

      <div className="right-side">
        <h2>Generated Test Cases</h2>
        <div className="output-content">
          {generatedTestCases || "Test cases will appear here after generation."}
        </div>
      </div>
    </div>
  );
}

export default App;
