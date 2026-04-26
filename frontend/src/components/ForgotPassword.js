import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

const API_BASE_URL = 'http://localhost:5000/api';

function ForgotPassword() {
  const [step, setStep] = useState(1); // 1: Request OTP, 2: Reset Password
  const [voterId, setVoterId] = useState('');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRequestOtp = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: 'info', message: 'Verifying credentials and sending OTP...' });

    try {
      const response = await axios.post(`${API_BASE_URL}/forgot-password`, {
        voter_id: voterId,
        email: email
      });

      setStatus({ type: 'success', message: response.data.message });
      setStep(2);
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.response?.data?.error || 'Failed to request OTP. Please check your Voter ID and Email.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setStatus({ type: 'error', message: 'Passwords do not match' });
      return;
    }

    setLoading(true);
    setStatus({ type: 'info', message: 'Resetting password...' });

    try {
      const response = await axios.post(`${API_BASE_URL}/reset-password`, {
        voter_id: voterId,
        otp: otp,
        new_password: newPassword
      });

      setStatus({ type: 'success', message: response.data.message });
      
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.response?.data?.error || 'Failed to reset password. Please check the OTP.'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card fade-in" style={{ maxWidth: '500px', margin: '60px auto' }}>
      <h1 className="card-title">{step === 1 ? 'Forgot Password' : 'Reset Password'}</h1>
      <p className="subtitle" style={{ marginBottom: '30px', color: 'var(--text-muted)' }}>
        {step === 1 
          ? 'Enter your registered Voter ID and Email to receive a 6-digit recovery code.' 
          : 'Enter the OTP sent to your email and choose a new password.'}
      </p>

      {step === 1 ? (
        <form onSubmit={handleRequestOtp}>
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
            <label htmlFor="email">Registered Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="john@example.com"
              required
            />
          </div>

          {status.message && (
            <div className={`notice notice-${status.type}`}>
              {status.message}
            </div>
          )}

          <button type="submit" disabled={loading} style={{ width: '100%', marginTop: '10px' }}>
            {loading ? 'Sending...' : 'Send OTP'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleResetPassword}>
          <div className="form-group">
            <label htmlFor="otp">Enter 6-digit OTP</label>
            <input
              type="text"
              id="otp"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              placeholder="123456"
              maxLength="6"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="newPassword">New Password</label>
            <input
              type="password"
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm New Password</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          {status.message && (
            <div className={`notice notice-${status.type}`}>
              {status.message}
            </div>
          )}

          <button type="submit" disabled={loading} style={{ width: '100%', marginTop: '10px' }}>
            {loading ? 'Updating...' : 'Reset Password'}
          </button>
          
          <button 
            type="button" 
            onClick={() => setStep(1)} 
            className="btn-secondary" 
            style={{ width: '100%', marginTop: '10px' }}
          >
            Back
          </button>
        </form>
      )}

      <div className="card-footer" style={{ marginTop: '30px', textAlign: 'center', fontSize: '14px' }}>
        <p>Remember your password? <Link to="/login" style={{ color: 'var(--accent)', fontWeight: '600' }}>Login here</Link></p>
      </div>
    </div>
  );
}

export default ForgotPassword;
