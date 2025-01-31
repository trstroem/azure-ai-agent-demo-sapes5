import React, { useState } from "react";
import ProductInput from "./components/ProductInput";
import StepProgress from "./components/StepProgress";
import { analyzeProduct } from "./api";
import ResultsDisplay from "./components/ResultsDisplay";

const App = () => {
  const [progress, setProgress] = useState([
    { id: 1, name: "Enter Product ID", completed: true },
    { id: 2, name: "Retrieve Product & Reviews", completed: false },
    { id: 3, name: "Create Thread", completed: false },
    { id: 4, name: "Run Workflow", completed: false },
    { id: 5, name: "Show Summary & Charts", completed: false },
    { id: 6, name: "Delete Agent", completed: false },
    { id: 7, name: "Save Results Locally", completed: false },
  ]);
  const [chatWindow, setChatWindow] = useState([]);
  const [systemProgress, setSystemProgress] = useState([]);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Update progress step
  const updateProgress = (id) => {
    setProgress((prevProgress) =>
      prevProgress.map((step) =>
        step.id === id ? { ...step, completed: true } : step
      )
    );
  };

  // Add a message to the chat window
  const addChatMessage = (message) => {
    setChatWindow((prevMessages) => [...prevMessages, message]);
  };

  // Add a message to the system progress
  const addSystemProgress = (message) => {
    setSystemProgress((prevMessages) => [...prevMessages, message]);
  };

  const handleAnalyzeProduct = async (productId) => {
    setError(null);
    setResults(null);

    try {
      addSystemProgress(`Starting analysis for Product ID: ${productId}`);
      updateProgress(2); // Mark "Retrieve Product & Reviews" as completed

      // Call to backend API
      const response = await analyzeProduct(productId, (message) =>
        addSystemProgress(message)
      );

      if (response && response.status === "success") {
        addSystemProgress("Analysis completed successfully.");
        updateProgress(3); // Mark "Create Thread" as completed
        updateProgress(4); // Mark "Run Workflow" as completed
        updateProgress(5); // Mark "Show Summary & Charts" as completed
        setResults(response); // Pass the full response to ResultsDisplay
        addChatMessage("System: Results are ready to view.");
      } else {
        throw new Error("Unexpected response from the backend.");
      }
    } catch (err) {
      setError(err.message || "An error occurred.");
      addSystemProgress(`Error: ${err.message || "An error occurred."}`);
      addChatMessage(`Error: ${err.message || "An error occurred."}`);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Azure AI Agent Service for SAP ES5 Products</h1>
        <p>Analyze SAP products with reviews and visualize insights</p>
      </header>
      <div className="App-container">
        {/* Left Column */}
        <div className="App-left">
          <StepProgress progress={progress} />
          <ProductInput onAnalyze={handleAnalyzeProduct} />
        </div>
        {/* Right Column */}
        <div className="App-right">
          <div className="Right-column-container">
            <div className="ChatWindow">
              <h3>Chat Window</h3>
              <ul>
                {chatWindow.map((message, index) => (
                  <li key={index}>{message}</li>
                ))}
              </ul>
            </div>
            <div className="SystemProgress">
              <h3>System Progress</h3>
              <ul>
                {systemProgress.map((message, index) => (
                  <li key={index}>{message}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Show Results when available */}
          {results && <ResultsDisplay results={results} />}
        </div>
      </div>
      <footer>&copy; 2025 Azure AI Service Agent Demo by chanpark@MSFT</footer>
    </div>
  );
};

export default App;
