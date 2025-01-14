import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = ({ setToken }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');  // Clear token on logout
    setToken(null);  // Update App state
    navigate('/login');  // Redirect to login page
  };

  return (
    <nav className="navbar">
      <ul>
        <li>
          <Link to="/stockpicker">Stock Picker</Link>
        </li>
        <li>
          <Link to="/portfolio">Portfolio</Link>
        </li>
        <li>
          <Link to="/tradehistory">Trade History</Link>
        </li>
        <li>
          <button onClick={handleLogout}>Logout</button>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
