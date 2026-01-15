import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

function Admin() {
  const [votes, setVotes] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchVotes = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/votes`);
      setVotes(response.data.votes || []);
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch votes');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/stats`);
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  useEffect(() => {
    fetchVotes();
    fetchStats();
    
    // Refresh votes every 5 seconds for real-time updates
    const interval = setInterval(() => {
      fetchVotes();
      fetchStats();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
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
        <h1>Admin Dashboard</h1>
        
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

