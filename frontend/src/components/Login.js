import React, { useState } from 'react';
import axios from 'axios';
import API_BASE_URL from '../apiConfig';

function Login({ onLoginSuccess }) {
  const [voterId, setVoterId] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!voterId || !password) {
      setStatus({ type: 'error', message: 'Please fill in all fields' });
      return;
    }

    setIsProcessing(true);
    setStatus({ type: 'info', message: 'Authenticating...' });

    try {
      const response = await axios.post(`${API_BASE_URL}/login`, {
        voter_id: voterId,
        password: password
      });

      setStatus({ type: 'success', message: 'Login successful!' });
      
      // Notify parent component about success
      if (onLoginSuccess) {
        onLoginSuccess(response.data.voter);
      }
      
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.response?.data?.error || 'Login failed. Please check your credentials.'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="login-container">
      <h1>Voter Login</h1>
      <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '30px' }}>
        Please enter your credentials to access the voting portal.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="loginVoterId">Voter ID</label>
          <input
            type="text"
            id="loginVoterId"
            value={voterId}
            onChange={(e) => setVoterId(e.target.value)}
            placeholder="Enter your Voter ID"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="loginPassword">Password</label>
          <input
            type="password"
            id="loginPassword"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
          />
        </div>

        {status.message && (
          <div className={`status-message status-${status.type}`}>
            {status.message}
          </div>
        )}

        <div style={{ textAlign: 'center', marginTop: '30px' }}>
          <button type="submit" disabled={isProcessing}>
            {isProcessing ? 'Logging in...' : 'Login'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default Login;
