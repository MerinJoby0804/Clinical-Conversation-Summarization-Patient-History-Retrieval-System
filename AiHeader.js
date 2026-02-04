import React from "react";
import "./AiHeader.css";

function AiHeader({ title, onBack }) {
  return (
    <div className="ai-header">
      <button className="ai-back" onClick={onBack}>
        ← Change Role
      </button>

      <h1>{title}</h1>
    </div>
  );
}

export default AiHeader;
