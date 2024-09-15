import React from 'react';

const PolicySuggestions = ({ suggestions }) => {
  return (
    <div>
      <h3>Suggested Technical Policies:</h3>
      <ul>
        {suggestions.map((suggestion, index) => (
          <li key={index}>{suggestion}</li>
        ))}
      </ul>
    </div>
  );
};

export default PolicySuggestions
