import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');

  if (!token) {
    return <Navigate to="/login" />;
  }

  try {
    // Optionally decode and validate the token here if needed
    // Example: jwt.decode(token) or check expiration
    return children;
  } catch (error) {
    console.error('Invalid token:', error);
    localStorage.removeItem('token'); // Remove invalid token
    return <Navigate to="/login" />;
  }
};

export default ProtectedRoute;
