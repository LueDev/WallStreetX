import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import StockPicker from './StockPicker';
import Portfolio from './Portfolio';
import TradeHistory from './TradeHistory';
import Navbar from './Navbar';  // Import Navbar
import ProtectedRoute from './ProtectedRoute';
import Signup from './SignUp';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  return (
    <Router>
      {token && <Navbar setToken={setToken} />}  {/* Show Navbar if token exists */}
      <Routes>
        <Route path="/" element={token ? <Navigate to="/stockpicker" /> : <Navigate to="/login" />} />
        <Route path="/login" element={<Login setToken={setToken} />} />
        <Route path="/signup" element={<Signup setToken={setToken} />} />
        <Route
          path="/stockpicker"
          element={
            <ProtectedRoute>
              <StockPicker />
            </ProtectedRoute>
          }
        />
        <Route
          path="/portfolio"
          element={
            <ProtectedRoute>
              <Portfolio />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tradehistory"
          element={
            <ProtectedRoute>
              <TradeHistory />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
