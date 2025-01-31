import axios from "axios";

const API_URL = "http://localhost:7071/analyze"; // Ensure this matches your backend's endpoint

// Function to analyze the product by ID
export const analyzeProduct = async (productId, onProgress) => {
  try {
    if (onProgress) onProgress("Starting product analysis...");

    // Axios GET request with improved error handling and timeout
    const response = await axios.get(`${API_URL}/${productId}`, {
      timeout: 15000, // 15 seconds timeout
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (onProgress) onProgress("Product analysis completed successfully!");

    return response.data; // Return the API response data
  } catch (error) {
    // Improved error handling
    let errorMessage;

    if (error.response) {
      // Server responded with a status code outside the range of 2xx
      errorMessage = `Error ${error.response.status}: ${
        error.response.data.message || error.response.data || "Unexpected error"
      }`;
    } else if (error.request) {
      // Request was made but no response received
      errorMessage = "No response from server. Possible network or CORS error.";
    } else {
      // Something else went wrong during the request setup
      errorMessage = `Request error: ${error.message}`;
    }

    console.error("Error fetching product analysis:", errorMessage);

    if (onProgress) onProgress("Failed to analyze product.");
    throw new Error(`Failed to analyze product. Details: ${errorMessage}`);
  }
};
