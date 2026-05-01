import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Voting from './Voting';
import './Home.css';

const Home = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [voter, setVoter] = useState(null);
    const [isScrolled, setIsScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const voterId = localStorage.getItem('voter_id');
        const voterName = localStorage.getItem('voter_name');
        if (voterId) {
            setVoter({ id: voterId, name: voterName });
        }

        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('voter_id');
        localStorage.removeItem('voter_name');
        localStorage.removeItem('voter_slip');
        setVoter(null);
        setActiveTab('overview');
        navigate('/');
    };

    const handleVoteClick = () => {
        if (voter) {
            setActiveTab('voting');
        } else {
            navigate('/login');
        }
    };

    const handleRegisterClick = () => {
        navigate('/register');
    };

    const handleLoginClick = () => {
        navigate('/login');
    };

    return (
        <div className="home-container">
            {/* Top Navbar */}
            <nav className={`navbar ${isScrolled ? 'scrolled' : ''}`}>
                <div className="nav-container wrapper">
                    <div className="logo-section" onClick={() => setActiveTab('overview')} style={{ cursor: 'pointer' }}>
                        <img src="/assets/logo.jpeg" alt="Logo" className="nav-logo-img" />
                        <span className="logo-text">NYAYA <span className="text-blue">VOTE</span></span>
                    </div>

                    {activeTab === 'overview' && (
                        <div className={`nav-links ${mobileMenuOpen ? 'mobile-open' : ''}`}>
                            <a href="#top" className="active" onClick={() => setMobileMenuOpen(false)}>Home</a>
                            <a href="#about" onClick={() => setMobileMenuOpen(false)}>About Us</a>
                            <a href="#features" onClick={() => setMobileMenuOpen(false)}>Features</a>
                            <a href="#services" onClick={() => setMobileMenuOpen(false)}>Services</a>
                            <button className="nav-btn-link" onClick={() => { handleVoteClick(); setMobileMenuOpen(false); }}>Vote</button>
                        </div>
                    )}

                    <div className="nav-actions">
                        {voter ? (
                            <div className="user-menu">
                                <span className="voter-name-nav" style={{ marginRight: '15px', fontWeight: '600', color: (isScrolled || mobileMenuOpen) ? '#1e293b' : 'white' }}>{voter.name}</span>
                                <button className="btn-outline-blue" onClick={handleLogout} style={{ borderColor: (isScrolled || mobileMenuOpen) ? '#2563eb' : 'white', color: (isScrolled || mobileMenuOpen) ? '#2563eb' : 'white' }}>Logout</button>
                            </div>
                        ) : (
                            <div className="auth-nav-group">
                                <button onClick={handleLoginClick} className="btn-outline-white-nav" style={{ marginRight: '10px' }}>Login</button>
                                <button onClick={handleRegisterClick} className="btn-primary-nav">Register</button>
                            </div>
                        )}

                        {/* Mobile Menu Toggle */}
                        {activeTab === 'overview' && (
                            <button className="mobile-menu-toggle" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
                                <span className="burger-bar" style={{ backgroundColor: (isScrolled || mobileMenuOpen) ? '#1e293b' : 'white' }}></span>
                                <span className="burger-bar" style={{ backgroundColor: (isScrolled || mobileMenuOpen) ? '#1e293b' : 'white' }}></span>
                                <span className="burger-bar" style={{ backgroundColor: (isScrolled || mobileMenuOpen) ? '#1e293b' : 'white' }}></span>
                            </button>
                        )}
                    </div>
                </div>
            </nav>

            {activeTab === 'overview' ? (
                <div className="overview-content">
                    {/* Hero Section */}
                    <header id="top" className="hero-section" style={{ backgroundImage: "url('/assets/hero_bg.jpeg')" }}>
                        <div className="hero-overlay"></div>
                        <div className="hero-content wrapper">
                            <div className="hero-text-area">
                                <div className="tag-badge">Secure • Transparent • Trusted</div>
                                <h1 className="hero-title">Your Voice.<br /><span className="text-blue">Your Power.</span></h1>
                                <p className="hero-subtitle">
                                    NYAYA VOTE is a secure and easy-to-use online voting platform built for fairness, transparency, and a better democracy.
                                </p>
                                <div className="hero-buttons">
                                    {voter ? (
                                        <button className="btn-primary" onClick={handleVoteClick}>
                                            <span className="icon-vote">🗳️</span> Go to Voting Booth
                                        </button>
                                    ) : (
                                        <>
                                            <button className="btn-primary" onClick={handleRegisterClick}>
                                                Register Now
                                            </button>
                                            <button className="btn-outline-white" onClick={handleLoginClick}>
                                                Log In to Vote
                                            </button>
                                        </>
                                    )}
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* About Section - A Smarter Way */}
                    <section id="about" className="smarter-way wrapper">
                        <div className="smarter-text">
                            <h5 className="section-subtitle">WELCOME TO NYAYA VOTE</h5>
                            <h2>A Smarter Way to Vote</h2>
                            <p>
                                We make voting simple, secure, and accessible for everyone. Whether it's college elections, organization polls, or community decisions — NYAYA VOTE ensures every vote counts.
                            </p>
                            <button className="btn-primary" onClick={handleRegisterClick}>Get Started Today</button>
                        </div>
                        <div className="smarter-image">
                            <div className="laptop-graphic">
                                <div className="laptop-screen">
                                    <div className="laptop-content">
                                        <div className="user-icon" style={{ fontSize: '4rem', marginBottom: '15px' }}>👤</div>
                                        <div className="btn-fake" style={{ background: '#2563eb', color: 'white', padding: '10px 20px', borderRadius: '4px', fontWeight: 'bold' }}>SUBMIT VOTE</div>
                                    </div>
                                    <div className="shield-icon">🛡️</div>
                                </div>
                                <div className="laptop-base"></div>
                            </div>
                        </div>
                    </section>

                    {/* Features Section */}
                    <section id="features" className="features-section">
                        <div className="wrapper">
                            <div className="section-header center">
                                <h5 className="section-subtitle">WHY CHOOSE NYAYA VOTE?</h5>
                                <h2>Trusted by Users, <span className="text-blue">Built for Democracy</span></h2>
                            </div>
                            <div className="features-grid">
                                <div className="feature-card">
                                    <div className="feature-icon">🛡️</div>
                                    <h4>Secure & Safe</h4>
                                    <p>Advanced security protects your identity and vote.</p>
                                </div>
                                <div className="feature-card">
                                    <div className="feature-icon">👥</div>
                                    <h4>One Person One Vote</h4>
                                    <p>Prevents duplicate voting and ensures fairness.</p>
                                </div>
                                <div className="feature-card">
                                    <div className="feature-icon">⏱️</div>
                                    <h4>Easy & Fast</h4>
                                    <p>Simple process that takes just a few minutes.</p>
                                </div>
                                <div className="feature-card">
                                    <div className="feature-icon">📊</div>
                                    <h4>Admin Control</h4>
                                    <p>Managed and monitored by authorized admins.</p>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* How It Works Section */}
                    <section id="services" className="how-it-works wrapper">
                        <div className="section-header center">
                            <h5 className="section-subtitle">HOW IT WORKS</h5>
                            <h2>Voting Made <span className="text-blue">Simple</span></h2>
                            <p className="section-desc" style={{ marginBottom: '60px', color: '#64748b' }}>Cast your vote in just three easy steps.</p>
                        </div>
                        <div className="steps-container">
                            <div className="step-item">
                                <div className="step-icon">👤</div>
                                <div className="step-number">01</div>
                                <h4>Login & Verify</h4>
                                <p>Secure login and identity verification.</p>
                            </div>
                            <div className="step-item">
                                <div className="step-icon">📋</div>
                                <div className="step-number">02</div>
                                <h4>Choose & Vote</h4>
                                <p>Select your candidate and submit your vote.</p>
                            </div>
                            <div className="step-item">
                                <div className="step-icon">✅</div>
                                <div className="step-number">03</div>
                                <h4>Confirmation</h4>
                                <p>Get instant confirmation that your vote is recorded.</p>
                            </div>
                        </div>
                    </section>

                    {/* CTA Banner */}
                    <section className="cta-banner wrapper">
                        <div className="cta-content">
                            <div>
                                <h2>Ready to Make a Difference?</h2>
                                <p>Your vote shapes the future. Don't miss your chance to participate.</p>
                            </div>
                            <button className="btn-primary" onClick={handleVoteClick} style={{ background: 'white', color: '#2563eb' }}>
                                <span className="icon-vote">🗳️</span> Vote Now
                            </button>
                        </div>
                    </section>

                    {/* Footer */}
                    <footer className="site-footer">
                        <div className="wrapper footer-grid">
                            <div className="footer-col brand-col">
                                <h3 className="footer-logo">NYAYA <span className="text-blue">VOTE</span></h3>
                                <p>Empowering Democracy Through Secure Online Voting.</p>
                            </div>
                            <div className="footer-col links-col">
                                <h4>Quick Links</h4>
                                <ul>
                                    <li><a href="#top">Home</a></li>
                                    <li><a href="#about">About Us</a></li>
                                    <li><a href="#features">Features</a></li>
                                    <li><a href="#services">Services</a></li>
                                    <li><button className="footer-btn-link" onClick={handleVoteClick}>Vote</button></li>
                                </ul>
                            </div>
                            <div className="footer-col contact-col">
                                <h4>Contact</h4>
                                <ul>
                                    <li>support@nyayavote.com</li>
                                    <li>Hyderabad, Telangana, India</li>
                                </ul>
                            </div>
                            <div className="footer-col social-col">
                                <h4>Follow Us</h4>
                                <div className="social-icons">
                                    <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" className="social-btn">f</a>
                                    <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-btn">t</a>
                                    <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="social-btn">in</a>
                                </div>
                            </div>
                        </div>
                        <div className="footer-bottom wrapper">
                            <p className="footer-bottom-text">© 2024 NYAYA VOTE. All rights reserved.</p>
                        </div>
                    </footer>
                </div>
            ) : (
                <div className="voting-tab-container">
                    <div className="voting-header wrapper">
                        <button className="btn-outline-blue" onClick={() => setActiveTab('overview')}>
                            ← Back to Home
                        </button>
                        {voter && <div className="voter-status">Authenticated as: <strong>{voter.id}</strong></div>}
                    </div>
                    <Voting />
                </div>
            )}
        </div>
    );
};

export default Home;
