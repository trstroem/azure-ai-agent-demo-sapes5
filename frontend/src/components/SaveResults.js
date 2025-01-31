import React from "react";

const SaveResults = ({ results }) => {
  const handleSave = () => {
    const blob = new Blob([JSON.stringify(results, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "product_analysis_results.json";
    link.click();
  };

  return (
    <div>
      <h2>Step 6: Save Results</h2>
      <button onClick={handleSave}>Save Results Locally</button>
    </div>
  );
};

export default SaveResults;
