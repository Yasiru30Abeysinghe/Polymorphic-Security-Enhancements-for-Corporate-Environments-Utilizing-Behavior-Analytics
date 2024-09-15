import React, { useState } from "react";

function InputForm({ onSend }) {
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState([]); // Holds all chat-like messages
  const [configurations, setConfigurations] = useState({}); // To store user configurations for each policy

  const handleChange = (event) => {
    setInputText(event.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Add user input as a message in the chat
    const userMessage = { sender: "user", content: inputText };
    setMessages((prevMessages) => [...prevMessages, userMessage]);

    try {
      // 1. Send input to the NLP backend for initial analysis and policy suggestions
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
      console.log("Backend response (NLP Analysis):", data);

      // Add system message with the analysis result
      const systemMessage = { sender: "system", content: `Analyzed: ${data.message}` };
      setMessages((prevMessages) => [...prevMessages, systemMessage]);

      // 2. Call OpenAI API to get contextual explanations based on analysis
      const openAiResponse = await fetch("http://127.0.0.1:5000/openai", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ inputText: data.message }), // Send the analysis to OpenAI for further explanation
      });

      if (!openAiResponse.ok) {
        throw new Error(`HTTP error! status: ${openAiResponse.status}`);
      }

      const openAiData = await openAiResponse.json();
      const openAiMessage = { sender: "system", content: `Explanation: ${openAiData.explanation}` };
      setMessages((prevMessages) => [...prevMessages, openAiMessage]);

      // 3. Set the suggested policies so we can configure them in the chat
      if (data.suggested_policies && data.suggested_policies.policies) {
        const policies = data.suggested_policies.policies; // Assuming backend returns structured data
        policies.forEach((policy) => {
          const policyMessage = { sender: "system", type: "policy", content: policy };
          setMessages((prevMessages) => [...prevMessages, policyMessage]);
        });
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "system", content: "An error occurred while processing your request." },
      ]);
    }
  };

  const handleConfigChange = (policyName, value) => {
    setConfigurations((prevConfigs) => ({
      ...prevConfigs,
      [policyName]: value,
    }));

    // Add message to show the user selection
    const selectionMessage = { sender: "user", content: `${policyName}: ${value}` };
    setMessages((prevMessages) => [...prevMessages, selectionMessage]);
  };

  const handleApplyPolicies = () => {
    console.log("Applying the following configurations:", configurations);
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: "system", content: "Policies applied successfully!" },
    ]);
  };

  const renderPolicyField = (policy) => {
    // Render different types of fields based on policy type in a chat-like manner
    switch (policy.type) {
      case "radio":
        return (
          <div key={policy.name} className="policy-config">
            <p>{policy.name}</p>
            {policy.options.map((option, index) => (
              <div key={index}>
                <input
                  type="radio"
                  id={`${policy.name}_${option}`}
                  name={policy.name}
                  value={option}
                  onChange={(e) => handleConfigChange(policy.name, e.target.value)}
                />
                <label htmlFor={`${policy.name}_${option}`}>{option}</label>
              </div>
            ))}
          </div>
        );
      case "text":
        return (
          <div key={policy.name} className="policy-config">
            <p>{policy.name}</p>
            <input
              type="text"
              name={policy.name}
              onChange={(e) => handleConfigChange(policy.name, e.target.value)}
            />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-bubble ${msg.sender}`}>
            {msg.content}
            {/* If it's a policy message, render the policy configuration */}
            {msg.type === "policy" && renderPolicyField(msg.content)}
          </div>
        ))}
      </div>

      {/* Chat input form */}
      <form onSubmit={handleSubmit} className="chat-input-form">
        <textarea
          value={inputText}
          onChange={handleChange}
          placeholder="Type in the security requirement..."
        />
        <button type="submit">Submit</button>
      </form>

      {/* Button to apply policies */}
      {Object.keys(configurations).length > 0 && (
        <button className="apply-policies-btn" onClick={handleApplyPolicies}>
          Apply Policies
        </button>
      )}
    </div>
  );
}

export default InputForm;
