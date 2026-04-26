import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

function Voting() {
  const [voterId, setVoterId] = useState(localStorage.getItem('voter_id') || '');
  const [step, setStep] = useState(localStorage.getItem('voter_id') ? 2 : 1); // Skip ID input if already logged in
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isProcessing, setIsProcessing] = useState(false);
  const [candidate, setCandidate] = useState('');
  const [candidates, setCandidates] = useState([]);
  const [voteToken, setVoteToken] = useState('');
  const [openEyeImage, setOpenEyeImage] = useState(null);

  const webcamRef = useRef(null);
  const [facingMode, setFacingMode] = useState('user');
  const blinkCheckInterval = useRef(null);

  useEffect(() => {
    fetchCandidates();

    // If we have a voterId from localStorage, set status to welcome them
    if (localStorage.getItem('voter_id')) {
      setStatus({ type: 'info', message: 'Welcome back! Please proceed with face verification.' });
    }

    // Cleanup interval on unmount
    return () => {
      if (blinkCheckInterval.current) {
        clearInterval(blinkCheckInterval.current);
      }
    };
  }, []);

  const fetchCandidates = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/candidates`);
      setCandidates(response.data.candidates || []);
    } catch (error) {
      console.error("Error fetching candidates:", error);
      setStatus({ type: 'error', message: 'Failed to load candidates.' });
    }
  };

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      return imageSrc;
    }
    return null;
  }, [webcamRef]);

  const handleFaceVerification = async () => {
    const imageSrc = capture();
    if (!imageSrc) {
      setStatus({ type: 'error', message: 'Failed to capture image' });
      return;
    }

    setIsProcessing(true);
    setStatus({ type: 'info', message: 'Verifying face ...' });

    try {
      const response = await axios.post(`${API_BASE_URL}/verify`, {
        voter_id: voterId,
        face_image: imageSrc,
      });

      if (response.data.verified) {
        setStatus({
          type: 'success',
          message: `Face verified successfully! (Confidence: ${response.data.confidence}%)`
        });
        setOpenEyeImage(imageSrc); // Store the verified face (Open Eyes)
        setStep(3); // Move to liveness detection
        startBlinkDetection(imageSrc);
      }
    } catch (error) {
      const errorData = error.response?.data;
      let msg = errorData?.error || 'Verification failed. Please try again.';

      if (errorData?.confidence !== undefined) {
        msg += ` (Confidence: ${errorData.confidence}%)`;
      }

      setStatus({
        type: 'error',
        message: msg
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const startBlinkDetection = (initialOpenImage) => {
    setStatus({ type: 'info', message: 'Please blink your eyes naturally...' });

    let checkCount = 0;
    // Check for blinks every 1 second
    blinkCheckInterval.current = setInterval(async () => {
      checkCount++;
      if (checkCount % 3 === 0) {
        setStatus({ type: 'info', message: 'Analyzing face... Please blink naturally.' });
      } else if (checkCount % 3 === 1) {
        setStatus({ type: 'info', message: 'Keep your eyes visible to the camera...' });
      }

      const imageSrc = capture();
      if (imageSrc) {
        try {
          // First check for simple blink/liveness
          const response = await axios.post(`${API_BASE_URL}/liveness`, {
            face_image: imageSrc
          });

          if (response.data.liveness_detected) {
            // Blink detected! Now perform Secure Verification
            if (blinkCheckInterval.current) {
              clearInterval(blinkCheckInterval.current);
            }

            setStatus({ type: 'info', message: 'Blink detected! Verifying security...' });

            performSecureVerify(initialOpenImage || openEyeImage, imageSrc);
          }
        } catch (error) {
          console.error('Liveness check error:', error);
        }
      }
    }, 1000);
  };

  const performSecureVerify = async (imgOpen, imgClosed) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/secure_verify`, {
        voter_id: voterId,
        image_open: imgOpen,
        image_closed: imgClosed
      });

      if (response.data.verified) {
        setVoteToken(response.data.vote_token);
        setStatus({
          type: 'success',
          message: 'Security verification passed! You may now vote.'
        });
        setStep(4);
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Secure verification failed.';
      setStatus({ type: 'error', message: errorMsg });
      // Optional: restart blink detection or force reset
      setTimeout(reset, 3000);
    }
  };

  const handleVote = async (e) => {
    e.preventDefault();

    if (!candidate) {
      setStatus({ type: 'error', message: 'Please select a candidate' });
      return;
    }

    if (!voteToken) {
      setStatus({ type: 'error', message: 'Security token missing. Please restart verification.' });
      return;
    }

    setIsProcessing(true);
    setStatus({ type: 'info', message: 'Casting your vote...' });

    try {
      const response = await axios.post(`${API_BASE_URL}/vote`, {
        vote_token: voteToken,
        candidate: candidate,
        vote_data: {}
      });

      setStatus({ type: 'success', message: response.data.message || 'Vote cast successfully!' });
      setVoterId('');
      setCandidate('');
      setVoteToken('');
      setOpenEyeImage(null);
      setStep(1);
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.response?.data?.error || 'Failed to cast vote. Please try again.'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const reset = () => {
    setStep(1);
    setStatus({ type: '', message: '' });
    setVoteToken('');
    setOpenEyeImage(null);
    if (blinkCheckInterval.current) {
      clearInterval(blinkCheckInterval.current);
    }
  };

  return (
    <div className="card fade-in">
      <h1 className="card-title">Secure Voting Terminal</h1>

      {step === 1 && (
        <form onSubmit={(e) => {
          e.preventDefault();
          if (!voterId) {
            setStatus({ type: 'error', message: 'Please enter your voter ID' });
            return;
          }

          setStep(2);
        }}>
          <div className="form-group">
            <label htmlFor="voterId">Voter ID *</label>
            <input
              type="text"
              id="voterId"
              value={voterId}
              onChange={(e) => setVoterId(e.target.value)}
              placeholder="e.g. V123456"
              required
            />
          </div>

          <button type="submit" disabled={!voterId} style={{ width: '100%' }}>
            Continue to Face Verification
          </button>
        </form>
      )}

      {step === 2 && (
        <div>
          <h2>Face Identity Verification</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>
            Looking directly at the camera to verify your biometric profile.
          </p>
          <div className="video-container">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={{
                facingMode: facingMode,
                width: 640,
                height: 480
              }}
            />
          </div>
          <div style={{ textAlign: 'center', marginTop: '20px', display: 'flex', gap: '10px' }}>
            <button onClick={handleFaceVerification} disabled={isProcessing} style={{ flex: 2 }}>
              {isProcessing ? 'Verifying...' : 'Verify Face'}
            </button>
            <button onClick={() => setFacingMode(facingMode === 'user' ? 'environment' : 'user')} className="secondary" style={{ flex: 1 }}>
              Flip
            </button>
            <button onClick={reset} className="secondary" style={{ flex: 1 }}>Reset</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div>
          <h2>Liveness Detection</h2>
          <p style={{ marginBottom: '15px', color: 'var(--text-muted)' }}>
            Please blink your eyes naturally. This ensures you are a live person.
          </p>
          <div className="video-container">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={{
                facingMode: facingMode,
                width: 640,
                height: 480
              }}
            />
          </div>
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <button onClick={reset} className="secondary">Restart Process</button>
          </div>
        </div>
      )}

      {step === 4 && (
        <form onSubmit={handleVote}>
          <h2>Cast Your Official Vote</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '25px' }}>
            Select your preferred candidate from the list below.
          </p>
          <div className="form-group">
            <label>Candidates *</label>
            <div className="candidates-list" style={{ marginTop: '15px' }}>
              {candidates.length > 0 ? (
                candidates.map((cand) => (
                  <label key={cand.id} style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    padding: '15px', 
                    border: '1px solid var(--border-light)', 
                    borderRadius: '4px',
                    marginBottom: '10px', 
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }} 
                  className="candidate-option">
                    <input
                      type="radio"
                      name="candidate"
                      value={cand.name}
                      checked={candidate === cand.name}
                      onChange={(e) => setCandidate(e.target.value)}
                      style={{ marginRight: '15px', width: '18px', height: '18px' }}
                    />
                    <div>
                      <div style={{ fontWeight: '700', fontSize: '15px' }}>{cand.name}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{cand.party}</div>
                    </div>
                  </label>
                ))
              ) : (
                <div className="notice notice-warning">No candidates available. Please contact admin.</div>
              )}
            </div>
          </div>

          <div style={{ textAlign: 'center', marginTop: '30px', borderTop: '1px solid var(--border-light)', paddingTop: '20px' }}>
            <button type="submit" disabled={isProcessing || !candidate} style={{ width: '100%', padding: '15px' }}>
              {isProcessing ? 'Casting Vote...' : 'Confirm & Cast Vote'}
            </button>
            <button type="button" onClick={reset} className="secondary" style={{ width: '100%', marginTop: '10px' }}>Cancel</button>
          </div>
        </form>
      )}

      {status.message && (
        <div className={`notice notice-${status.type}`}>
          {status.message}
        </div>
      )}
    </div>
  );
}

export default Voting;
