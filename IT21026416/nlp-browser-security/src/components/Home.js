import React, { useState } from 'react';
import ChatWindow from './ChatWindow';
import InputForm from './InputForm';
import './Home.css';

function Home() {
  const [messages, setMessages] = useState([]);

  const addMessage = (newMessage) => {
    setMessages([...messages, newMessage]);
  };

  return (
    <div className="home-container">
      <div className="chat-window">
        <ChatWindow messages={messages} />
      </div>
      <InputForm onSend={addMessage} />
    </div>
  );
}

export default Home;
