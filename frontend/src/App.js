import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Registration from './components/Registration';
import Voting from './components/Voting';
import Admin from './components/Admin';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
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

