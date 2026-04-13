import React from 'react';

function Home({ isLoggedIn, voterName, onLaunchLogin, onLaunchRegister, onGoToVote }) {

  return (
    <div className="home-container">
      {/* ── Hero ── */}
      <section className="hero">
        <div className="hero-bg-overlay"></div>
        <div className="hero-content">
          <h1>NyayaVote System</h1>
          <p className="hero-subtitle">
            Next-generation biometric election platform. Secure, transparent, and tamper-proof voting for the modern era.
          </p>

          {isLoggedIn ? (
            <div className="hero-actions">
              <div className="welcome-box">
                <h2>Welcome back, {voterName}!</h2>
                <p>Your identity is verified. You are ready to participate in the active election.</p>
                <button className="cta-button primary" onClick={onGoToVote}>
                  Go to Voting Booth
                </button>
              </div>
            </div>
          ) : (
            <div className="hero-actions">
              <button className="cta-button hero-small-btn primary" onClick={onLaunchLogin}>
                Voter Login
              </button>
              <button className="cta-button hero-small-btn secondary" onClick={onLaunchRegister}>
                Register Now
              </button>
            </div>
          )}
        </div>
      </section>

      {/* ── Feature Cards ── */}
      <section className="features">
        <div className="feature-card">
          <div className="feature-icon">🛡️</div>
          <h3>Biometric Security</h3>
          <p>Multi-angle face recognition and liveness detection ensures that only you can cast your vote.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">⛓️</div>
          <h3>Encrypted Integrity</h3>
          <p>Every vote is securely encrypted and stored with high integrity to prevent tampering.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">⚡</div>
          <h3>Instant Process</h3>
          <p>Register and vote in minutes from anywhere, with immediate verification and feedback.</p>
        </div>
      </section>



      <footer className="footer">
        <p>&copy; 2026 NyayaVote System. All rights reserved.</p>
        <div className="footer-links">
          <a href="#privacy">Privacy Policy</a>
          <a href="#terms">Terms of Service</a>
          <a href="#help">Help Center</a>
        </div>
      </footer>
    </div>
  );
}

export default Home;
