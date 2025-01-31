import React from "react";

const ResultsDisplay = ({ results }) => {
  // If results or product summary is missing, show a fallback message
  if (!results || !results.product_summary) {
    return <div>No results available. Please try analyzing a product.</div>;
  }

  const { 
    product_summary: {
      product_name,
      description,
      price,
      average_rating,
      total_reviews,
      sentiment_analysis: { positive, negative, positive_summary, negative_summary },
    },
    bar_chart,
    pie_chart,
  } = results;

  // Correct the image URLs by removing extra /charts/ in the path
  const barChartUrl = bar_chart ? `http://localhost:7071/${bar_chart}` : "";
  const pieChartUrl = pie_chart ? `http://localhost:7071/${pie_chart}` : "";

  return (
    <div className="ResultsDisplay">
      <h3>Results</h3>
      <p><strong>Product Name:</strong> {product_name}</p>
      <p><strong>Description:</strong> {description}</p>
      <p><strong>Price:</strong> {price}</p>
      <p><strong>Average Rating:</strong> {average_rating}</p>
      <p><strong>Total Reviews:</strong> {total_reviews}</p>
      
      <h4>Sentiment Analysis</h4>
      <p><strong>Positive Reviews:</strong> {positive}</p>
      <p><strong>Negative Reviews:</strong> {negative}</p>
      <p><strong>Positive Summary:</strong> {positive_summary}</p>
      <p><strong>Negative Summary:</strong> {negative_summary}</p>

      <div className="Charts">
        <h4>Visualizations</h4>
        {barChartUrl && <img src={barChartUrl} alt="Bar Chart" />}
        {pieChartUrl && <img src={pieChartUrl} alt="Pie Chart" />}
      </div>
    </div>
  );
};

export default ResultsDisplay;
