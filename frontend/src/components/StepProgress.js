import React from "react";

const StepProgress = ({ progress }) => {
  return (
    <div className="ProgressBar">
      <ul>
        {progress.map((step) => (
          <li
            key={step.id}
            style={{
              color: step.completed ? "green" : "gray",
            }}
          >
            {step.completed ? "✔️" : "⏳"} {step.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default StepProgress;

