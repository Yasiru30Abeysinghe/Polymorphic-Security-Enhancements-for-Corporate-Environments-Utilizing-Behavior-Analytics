import React from 'react';
import './Header.css';

const Header = ({ onInputSubmit }) => {
  const handleInput = (e) => {
    e.preventDefault();
    const inputValue = e.target.querySelector('input').value;
    onInputSubmit(inputValue);
  };

};

export default Header;
