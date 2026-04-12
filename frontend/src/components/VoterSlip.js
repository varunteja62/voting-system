import React, { useState } from 'react';
import axios from 'axios';
import API_BASE_URL from '../apiConfig';

function VoterSlip() {
  const [voterId, setVoterId] = useState('');
  const [password, setPassword] = useState('');
  const [voterData, setVoterData] = useState(null);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isLoading, setIsLoading] = useState(false);

  const handleFetchSlip = async (e) => {
    e.preventDefault();
    if (!voterId || !password) {
      setStatus({ type: 'error', message: 'Please enter both Voter ID and Password' });
      return;
    }

    setIsLoading(true);
    setStatus({ type: 'info', message: 'Authenticating and fetching details...' });
    setVoterData(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/secure_voter_slip`, {
        voter_id: voterId,
        password: password
      });

      setVoterData(response.data);
      setStatus({ type: 'success', message: 'Voter details retrieved successfully!' });
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.response?.data?.error || 'Authentication failed. Please check your credentials.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div id="voter-slip-section">
      <div className="card no-print">
        <h1>Retrieve Voting Slip</h1>
        <p style={{ textAlign: 'center', marginBottom: '20px', color: 'var(--text-muted)' }}>
          Enter your credentials to generate your official voter identity slip.
        </p>
        
        <form onSubmit={handleFetchSlip}>
          <div className="form-group">
            <label htmlFor="voterId">Voter ID</label>
            <input
              type="text"
              id="voterId"
              value={voterId}
              onChange={(e) => setVoterId(e.target.value)}
              placeholder="e.g. V12345"
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
              placeholder="Your registered password"
              required
            />
          </div>

          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Processing...' : 'Generate Slip'}
          </button>
        </form>

        {status.message && (
          <div className={`status-message status-${status.type}`}>
            {status.message}
          </div>
        )}
      </div>

      {voterData && (
        <div className="slip-wrapper">
          <div className="voter-slip" id="voter-slip">
            <div className="slip-header">
              <div className="slip-logo-container">
                <span className="slip-logo-text">NYAYAVOTE</span>
              </div>
              <div className="slip-title">
                <h2>OFFICIAL VOTER SLIP</h2>
                <p>Digital Identity Verification Document</p>
              </div>
            </div>

            <div className="slip-body">
              <div className="voter-photo-section">
                <div className="voter-photo-frame">
                  {voterData.voter_image ? (
                    <img src={voterData.voter_image} alt="Voter" />
                  ) : (
                    <div className="photo-placeholder">PHOTO</div>
                  )}
                </div>
                <div className="verification-badge">VERIFIED</div>
              </div>

              <div className="voter-info-section">
                <div className="info-row">
                  <span className="info-label">VOTER NAME</span>
                  <span className="info-value">{voterData.name}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">VOTER ID</span>
                  <span className="info-value highlight">{voterData.voter_id}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">SIP UNIQUE STRING</span>
                  <span className="info-value sip-string">{voterData.slip_string}</span>
                </div>
              </div>
            </div>

            <div className="slip-footer">
              <div className="security-notice">
                <p><strong>Note:</strong> This SIP Unique String is required for the second factor of authentication during the voting process. Keep it confidential.</p>
              </div>
              <div className="slip-qr-placeholder">
                <div className="qr-box"></div>
                <span>SECURE SCAN</span>
              </div>
            </div>
          </div>
          
          <div className="slip-actions no-print">
            <button onClick={handlePrint} className="cta-button">
              Print / Download PDF
            </button>
            <p style={{ marginTop: '15px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              Tip: Save as PDF in the print dialog to keep a digital copy.
            </p>
          </div>
        </div>
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        .slip-wrapper {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin-top: 40px;
          animation: fadeUp 0.6s ease-out;
        }

        .voter-slip {
          background: white;
          color: #1e293b;
          width: 100%;
          max-width: 550px;
          border-radius: 0;
          padding: 40px;
          border: 1px solid #e2e8f0;
          box-shadow: 0 20px 50px rgba(0,0,0,0.1);
          position: relative;
          overflow: hidden;
        }

        .voter-slip::before {
          content: '';
          position: absolute;
          top: 0; left: 0; right: 0; height: 8px;
          background: linear-gradient(90deg, #4f46e5, #ec4899);
        }

        .slip-header {
          display: flex;
          align-items: center;
          gap: 25px;
          margin-bottom: 30px;
          border-bottom: 2px solid #f1f5f9;
          padding-bottom: 20px;
        }

        .slip-logo-text {
          font-weight: 900;
          font-size: 1.2rem;
          letter-spacing: 2px;
          color: #4f46e5;
          border: 2px solid #4f46e5;
          padding: 5px 10px;
        }

        .slip-title h2 {
          margin: 0;
          color: #0f172a;
          font-size: 1.5rem;
          border: none;
          padding: 0;
        }

        .slip-title p {
          margin: 0;
          font-size: 0.8rem;
          color: #64748b;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .slip-body {
          display: flex;
          gap: 30px;
          margin-bottom: 30px;
        }

        .voter-photo-section {
          flex: 0 0 160px;
          text-align: center;
        }

        .voter-photo-frame {
          width: 160px;
          height: 180px;
          border: 3px solid #f1f5f9;
          background: #f8fafc;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          margin-bottom: 10px;
        }

        .voter-photo-frame img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .verification-badge {
          background: #dcfce7;
          color: #15803d;
          font-size: 0.7rem;
          font-weight: 800;
          padding: 4px 10px;
          border-radius: 50px;
          display: inline-block;
        }

        .voter-info-section {
          flex: 1;
        }

        .info-row {
          margin-bottom: 20px;
        }

        .info-label {
          display: block;
          font-size: 0.7rem;
          font-weight: 700;
          color: #94a3b8;
          margin-bottom: 4px;
        }

        .info-value {
          display: block;
          font-size: 1.1rem;
          font-weight: 600;
          color: #1e293b;
        }

        .info-value.highlight {
          color: #4f46e5;
        }

        .info-value.sip-string {
          font-family: 'Courier New', monospace;
          background: #f1f5f9;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 1.4rem;
          letter-spacing: 3px;
          color: #ec4899;
          display: inline-block;
          border: 1px dashed #cbd5e1;
        }

        .slip-footer {
          display: flex;
          align-items: flex-end;
          gap: 20px;
          border-top: 1px solid #f1f5f9;
          padding-top: 20px;
        }

        .security-notice {
          flex: 1;
          font-size: 0.75rem;
          color: #64748b;
          line-height: 1.5;
        }

        .slip-qr-placeholder {
          flex: 0 0 80px;
          text-align: center;
        }

        .qr-box {
          width: 80px;
          height: 80px;
          background: #f1f5f9;
          border: 1px solid #e2e8f0;
          margin-bottom: 5px;
          /* Just for aesthetics */
          background-image: 
            linear-gradient(45deg, #ddd 25%, transparent 25%), 
            linear-gradient(-45deg, #ddd 25%, transparent 25%), 
            linear-gradient(45deg, transparent 75%, #ddd 75%), 
            linear-gradient(-45deg, transparent 75%, #ddd 75%);
          background-size: 10px 10px;
        }

        .slip-qr-placeholder span {
          font-size: 0.6rem;
          font-weight: 800;
          color: #94a3b8;
        }

        .slip-actions {
          margin-top: 30px;
          text-align: center;
          width: 100%;
          max-width: 550px;
        }

        @media print {
          .no-print {
            display: none !important;
          }
          body {
            background: white !important;
          }
          .voter-slip {
            box-shadow: none !important;
            border: 1px solid #ccc !important;
            margin: 0 !important;
            max-width: none !important;
          }
          .container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: none !important;
          }
        }
      `}} />
    </div>
  );
}

export default VoterSlip;
