import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Registration from './components/Registration';
import Voting from './components/Voting';
import Admin from './components/Admin';
import './App.css';

function App() {
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <Router>
      <div className={`App theme-${theme}`}>
        <nav className="nav">
          <ul className="nav-links">
            <li>
              <NavLink to="/register" className={({ isActive }) => isActive ? 'active' : ''}>
                Registration
              </NavLink>
            </li>
            <li>
              <NavLink to="/vote" className={({ isActive }) => isActive ? 'active' : ''}>
                Vote
              </NavLink>
            </li>
            <li>
              <NavLink to="/admin" className={({ isActive }) => isActive ? 'active' : ''}>
                Admin Dashboard
              </NavLink>
            </li>
          </ul>
          <button className="theme-toggle" onClick={toggleTheme} title="Toggle Dark/Light Mode">
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </nav>

        <div className="container">
          <Routes>
            <Route path="/register" element={<Registration />} />
            <Route path="/vote" element={<Voting />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/" element={<Registration />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;

