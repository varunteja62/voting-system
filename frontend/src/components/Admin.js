import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://varun62-voting-system-backend.hf.space/api';

function Admin() {
  const [votes, setVotes] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Auth state
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('adminToken'));
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');

  const handleLogout = useCallback(() => {
    localStorage.removeItem('adminToken');
    setIsAuthenticated(false);
    setVotes([]);
    setStats(null);
  }, []);

  const fetchVotes = useCallback(async () => {
    const token = localStorage.getItem('adminToken');
    if (!token) return;

    try {
      const response = await axios.get(`${API_BASE_URL}/admin/votes`, {
        headers: { 'Authorization': token }
      });
      setVotes(response.data.votes || []);
      setError('');
    } catch (err) {
      if (err.response?.status === 401) {
        handleLogout();
      } else {
        setError(err.response?.data?.error || 'Failed to fetch votes');
      }
    } finally {
      setLoading(false);
    }
  }, [handleLogout]);

  const fetchStats = useCallback(async () => {
    const token = localStorage.getItem('adminToken');
    if (!token) return;

    try {
      const response = await axios.get(`${API_BASE_URL}/admin/stats`, {
        headers: { 'Authorization': token }
      });
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAuthError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/admin/login`, {
        username,
        password
      });

      if (response.data.authenticated) {
        localStorage.setItem('adminToken', response.data.token);
        setIsAuthenticated(true);
        setError('');
      }
    } catch (err) {
      setAuthError(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchVotes();
      fetchStats();

      const interval = setInterval(() => {
        fetchVotes();
        fetchStats();
      }, 5000);

      return () => clearInterval(interval);
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, fetchVotes, fetchStats]);

  if (!isAuthenticated) {
    return (
      <div className="card">
        <h1>Admin Login</h1>
        <p style={{ textAlign: 'center', color: '#666', marginBottom: '20px' }}>
          Please enter admin credentials to view voting results.
        </p>
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="username">Admin Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
            />
          </div>

          {authError && (
            <div className="status-message status-error">
              {authError}
            </div>
          )}

          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <button type="submit" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </div>
        </form>
      </div>
    );
  }

  if (loading && votes.length === 0) {
    return (
      <div className="card">
        <h1>Admin Dashboard</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>Admin Dashboard</h1>
          <button onClick={handleLogout} className="secondary" style={{ height: 'fit-content' }}>
            Logout
          </button>
        </div>

        {stats && (
          <div className="stats-container">
            <div className="stat-card">
              <h3>Total Votes</h3>
              <div className="stat-value">{stats.total_votes}</div>
            </div>
            {stats.candidate_stats.map((stat, index) => (
              <div key={index} className="stat-card">
                <h3>{stat.candidate}</h3>
                <div className="stat-value">{stat.count}</div>
              </div>
            ))}
          </div>
        )}

        <div style={{ textAlign: 'right', marginBottom: '15px' }}>
          <button onClick={() => { fetchVotes(); fetchStats(); }}>
            Refresh
          </button>
        </div>

        {error && (
          <div className="status-message status-error">
            {error}
          </div>
        )}

        <h2>Real-Time Votes</h2>
        {votes.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
            No votes cast yet.
          </p>
        ) : (
          <table className="votes-table">
            <thead>
              <tr>
                <th>Voter ID</th>
                <th>Name</th>
                <th>Candidate</th>
                <th>Voted At</th>
              </tr>
            </thead>
            <tbody>
              {votes.map((vote, index) => (
                <tr key={index}>
                  <td>{vote.voter_id}</td>
                  <td>{vote.name}</td>
                  <td>{vote.candidate}</td>
                  <td>{new Date(vote.voted_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Admin;

