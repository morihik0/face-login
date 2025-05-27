import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';
import Register from './pages/Register';
import Authenticate from './pages/Authenticate';
import History from './pages/History';
import SignUp from './pages/SignUp';

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes without layout */}
        <Route path="/signup" element={<SignUp />} />
        
        {/* Protected routes with layout */}
        <Route path="/*" element={
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/users" element={<Users />} />
              <Route path="/register" element={<Register />} />
              <Route path="/authenticate" element={<Authenticate />} />
              <Route path="/history" element={<History />} />
            </Routes>
          </Layout>
        } />
      </Routes>
    </Router>
  );
}

export default App;