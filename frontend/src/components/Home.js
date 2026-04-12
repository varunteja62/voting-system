import React from 'react';
import VoterSlip from './VoterSlip';

function Home({ isLoggedIn, voterName, onLaunchLogin, onLaunchRegister, onGoToVote }) {
  return (
    <div className="home-container">
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
              <button className="cta-button primary" onClick={onLaunchLogin}>
                Voter Login
              </button>
              <button className="cta-button secondary" onClick={onLaunchRegister}>
                Register Now
              </button>
            </div>
          )}
        </div>
      </section>

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
      
      <VoterSlip />

      <section className="how-it-works">
        <h2>How it Works</h2>
        <div className="steps-container">
          <div className="step">
            <span className="step-number">1</span>
            <h4>Register</h4>
            <p>Create your profile and capture your biometric face map.</p>
          </div>
          <div className="step">
            <span className="step-number">2</span>
            <h4>Login</h4>
            <p>Securely sign in using your Voter ID and password.</p>
          </div>
          <div className="step">
            <span className="step-number">3</span>
            <h4>Verify</h4>
            <p>Complete a quick face check to confirm your identity at the polls.</p>
          </div>
          <div className="step">
            <span className="step-number">4</span>
            <h4>Vote</h4>
            <p>Select your candidate and securely cast your digital ballot.</p>
          </div>
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
