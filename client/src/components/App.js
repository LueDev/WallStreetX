import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './Login';
import StockPicker from './StockPicker';
import ProtectedRoute from './ProtectedRoute';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login setToken={setToken} />} />
        <Route
          path="/stockpicker"
          element={
            <ProtectedRoute>
              <StockPicker />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
