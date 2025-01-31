import React, { useState } from "react";

const ProductInput = ({ onAnalyze }) => {
  const [productId, setProductId] = useState("");
  const [loading, setLoading] = useState(false); // State to track loading
  const [error, setError] = useState(null); // State to track error message

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!productId) {
      setError("Please enter a valid Product ID.");
      return;
    }

    // Clear any previous errors
    setError(null);
    setLoading(true);

    try {
      // Trigger the analysis and pass loading state and error handling
      await onAnalyze(productId);
    } catch (err) {
      // Handle error if product analysis fails
      setError("Failed to analyze product. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Enter Product ID"
        value={productId}
        onChange={(e) => setProductId(e.target.value)}
        disabled={loading} // Disable input when loading
      />
      <button type="submit" disabled={loading}>
        {loading ? "Analyzing..." : "Analyze"} {/* Show loading text */}
      </button>

      {/* Display error message */}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </form>
  );
};

export default ProductInput;

