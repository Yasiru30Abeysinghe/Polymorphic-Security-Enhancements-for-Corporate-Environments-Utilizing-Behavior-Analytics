import React from 'react';
import './Header.css';

const Header = ({ onInputSubmit }) => {
  const handleInput = (e) => {
    e.preventDefault();
    const inputValue = e.target.querySelector('input').value;
    onInputSubmit(inputValue);
  };

  return (
    <header className="header">
      <form onSubmit={handleInput}>
        <input type="text" placeholder="Ask your security assistant..." />
        <button type="submit">Submit</button>
      </form>
    </header>
  );
};

export default Header;
