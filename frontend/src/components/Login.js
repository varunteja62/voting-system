import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

const API_BASE_URL = 'http://localhost:5000/api';

const Login = () => {
    const [voterId, setVoterId] = useState('');
    const [password, setPassword] = useState('');
    const [status, setStatus] = useState({ type: '', message: '' });
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setStatus({ type: 'info', message: 'Authenticating...' });

        try {
            const response = await axios.post(`${API_BASE_URL}/login`, {
                voter_id: voterId,
                password: password
            });

            if (response.status === 200) {
                setStatus({ type: 'success', message: 'Login successful! Redirecting to verification...' });
                // Store voter info in localStorage for the session
                localStorage.setItem('voter_id', response.data.voter.id);
                localStorage.setItem('voter_name', response.data.voter.name);
                localStorage.setItem('voter_slip', response.data.voter.slip_string);
                
                setTimeout(() => {
                    navigate('/');
                }, 1500);
            }
        } catch (error) {
            setStatus({
                type: 'error',
                message: error.response?.data?.error || 'Login failed. Please check your credentials.'
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card fade-in" style={{ maxWidth: '500px', margin: '60px auto' }}>
            <h1 className="card-title">Log In</h1>
            <p className="subtitle" style={{ marginBottom: '30px', color: 'var(--text-muted)' }}>
                Enter your credentials to access the voting terminal.
            </p>

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="voter_id">Voter ID</label>
                    <input
                        type="text"
                        id="voter_id"
                        value={voterId}
                        onChange={(e) => setVoterId(e.target.value)}
                        placeholder="e.g. V123456"
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
                        placeholder="••••••••"
                        required
                    />
                    <div style={{ textAlign: 'right', marginTop: '5px' }}>
                        <Link to="/forgot-password" style={{ fontSize: '12px', color: 'var(--accent)' }}>
                            Forgot Password?
                        </Link>
                    </div>
                </div>

                {status.message && (
                    <div className={`notice notice-${status.type}`}>
                        {status.message}
                    </div>
                )}

                <button type="submit" disabled={loading} style={{ width: '100%', marginTop: '10px' }}>
                    {loading ? 'Verifying...' : 'Log In'}
                </button>
            </form>

            <div className="card-footer" style={{ marginTop: '30px', textAlign: 'center', fontSize: '14px' }}>
                <p>Don't have an account? <Link to="/register" style={{ color: 'var(--accent)', fontWeight: '600' }}>Register here</Link></p>
            </div>
        </div>
    );
};

export default Login;
