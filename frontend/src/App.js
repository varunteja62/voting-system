import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Link } from 'react-router-dom';
import Registration from './components/Registration';
import Voting from './components/Voting';
import Admin from './components/Admin';
import Home from './components/Home';
import Login from './components/Login';
import Modal from './components/Modal';

import logo from './assets/images/logo.jpeg';
import './App.css';

function AppContent() {
  const [theme, setTheme] = useState('dark');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  
  const navigate = useNavigate();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const handleLoginSuccess = (userData) => {
    setIsLoggedIn(true);
    setUser(userData);
    setShowLoginModal(false);
    // After login, we stay on Home but now it shows the "Go to Vote" button
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUser(null);
    navigate('/');
  };

  const goToVote = () => {
    navigate('/vote');
  };

  return (
    <div className={`App theme-${theme}`}>
      <nav className="nav">
        <Link to="/" className="brand">
          <img src={logo} alt="NyayaVote Logo" className="brand-logo" />
          <span className="brand-text">NyayaVote</span>
        </Link>
        <ul className="nav-links">
          <li>
            <Link to="/" className="nav-item">Home</Link>
          </li>
          {isLoggedIn && (
            <li>
              <Link to="/vote" className="nav-item">Voting Booth</Link>
            </li>
          )}
          <li>
            <Link to="/admin" className="nav-item admin-link">Admin</Link>
          </li>
          {isLoggedIn ? (
            <li>
              <button onClick={handleLogout} className="logout-btn">Logout</button>
            </li>
          ) : (
            <li>
              <button onClick={() => setShowLoginModal(true)} className="login-btn">Login</button>
            </li>
          )}
        </ul>
        <button className="theme-toggle" onClick={toggleTheme} title="Toggle Dark/Light Mode">
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
      </nav>

      <div className="main-content">
        <Routes>
          <Route path="/" element={
            <Home 
              isLoggedIn={isLoggedIn} 
              voterName={user?.name} 
              onLaunchLogin={() => setShowLoginModal(true)}
              onLaunchRegister={() => setShowRegisterModal(true)}
              onGoToVote={goToVote}
            />
          } />
          <Route path="/vote" element={<Voting />} />
          <Route path="/admin" element={<Admin />} />

          {/* Legacy routes for direct access if needed */}
          <Route path="/register" element={<Registration />} />
        </Routes>
      </div>

      {/* Modals */}
      <Modal 
        isOpen={showLoginModal} 
        onClose={() => setShowLoginModal(false)} 
        title="Welcome Back"
      >
        <Login onLoginSuccess={handleLoginSuccess} />
      </Modal>

      <Modal 
        isOpen={showRegisterModal} 
        onClose={() => setShowRegisterModal(false)} 
        title="Create Voter Account"
      >
        <Registration />
      </Modal>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;

