import React, { useState } from 'react';
import './App.css';
import PolicyForm from './components/PolicyForm'; // Ensure the correct path

function App() {
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState([]);
  const [policyCategory, setPolicyCategory] = useState(null);

  const handleInputChange = (e) => {
    setInputText(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (inputText.trim() !== '') {
      try {
        const response = await fetch("http://127.0.0.1:5000/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ inputText }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setMessages([
          { text: `Analyzed: ${data.message}`, sender: 'system' },
          { text: `Classification: ${data.label}`, sender: 'system' },
          { text: `Justification: ${data.justification}`, sender: 'system' }
        ]);

        // Set the policy category (classification) for the form
        setPolicyCategory(data.label); 

      } catch (error) {
        setMessages(prevMessages => [
          ...prevMessages,
          { text: 'An error occurred while processing your request.', sender: 'system' }
        ]);
      }
    }
  };

 // const handleApplyPolicies = (finalConfigurations) => {
   // console.log("Applying the following configurations:", finalConfigurations);
    // Now send the final configurations to /generate for enforcement.
    //setMessages([...messages, { text: 'Policies applied successfully!', sender: 'system' }]);
  //};
  const handleApplyPolicies = async (formData) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setMessages(prevMessages => [
        ...prevMessages,
        { text: 'Policies applied successfully!', sender: 'system' }
      ]);

    } catch (error) {
      setMessages(prevMessages => [
        ...prevMessages,
        { text: 'An error occurred while applying policies.', sender: 'system' }
      ]);
    }
  };

  return (
    <div className="app-container">
      {/* Input and Display Logic */}
      <div className="main-content">
        <h1>Welcome to NLP Policy Generation</h1>
        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            placeholder="Enter high-level security requirement..."
            value={inputText}
            onChange={handleInputChange}
          />
          <button type="submit">Submit</button>
        </form>
        
        {/* Display the result */}
        <div className="chat-area">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-bubble ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
        </div>

        {/* Pass policy category to PolicyForm */}
        {policyCategory && (
          <PolicyForm policyCategory={policyCategory} 
          onApply={handleApplyPolicies} 
          />

        )}
      </div>
    </div>
  );
}

export default App;
