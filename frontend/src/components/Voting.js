import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

function Voting() {
  const [voterId, setVoterId] = useState('');
  const [step, setStep] = useState(1); // 1: ID input, 2: Face verify, 3: Liveness, 4: Vote
  const [capturedImage, setCapturedImage] = useState(null);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isProcessing, setIsProcessing] = useState(false);
  const [candidate, setCandidate] = useState('');
  const [candidates, setCandidates] = useState([]);
  const [blinkCount, setBlinkCount] = useState(0);
  const [blinkDetected, setBlinkDetected] = useState(false);

  const webcamRef = useRef(null);
  const [facingMode, setFacingMode] = useState('user');
  const blinkCheckInterval = useRef(null);

  useEffect(() => {
    fetchCandidates();

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
      setCapturedImage(imageSrc);
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
        setStatus({ type: 'success', message: 'Face verified successfully!' });
        setStep(3); // Move to liveness detection
        startBlinkDetection();
      }
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.response?.data?.error || 'Verification failed. Please try again.'
      });
      setCapturedImage(null);
    } finally {
      setIsProcessing(false);
    }
  };

  const startBlinkDetection = () => {
    setBlinkCount(0);
    setBlinkDetected(false);

    // Check for blinks every 2 seconds
    blinkCheckInterval.current = setInterval(async () => {
      const imageSrc = capture();
      if (imageSrc) {
        try {
          const response = await axios.post(`${API_BASE_URL}/liveness`, {
            face_image: imageSrc
          });

          if (response.data.liveness_detected) {
            setBlinkCount(prev => prev + 1);
            setBlinkDetected(true);
            setStatus({ type: 'success', message: `Blink detected! (${blinkCount + 1})` });

            // After detecting a blink, wait a moment then allow voting
            setTimeout(() => {
              if (blinkCheckInterval.current) {
                clearInterval(blinkCheckInterval.current);
              }
              setStep(4); // Move to voting step
              setStatus({ type: 'success', message: 'Liveness verified! You can now cast your vote.' });
            }, 1000);
          }
        } catch (error) {
          console.error('Liveness check error:', error);
        }
      }
    }, 2000);
  };

  const handleVote = async (e) => {
    e.preventDefault();

    if (!candidate) {
      setStatus({ type: 'error', message: 'Please select a candidate' });
      return;
    }

    setIsProcessing(true);
    setStatus({ type: 'info', message: 'Casting your vote...' });

    try {
      const response = await axios.post(`${API_BASE_URL}/vote`, {
        voter_id: voterId,
        candidate: candidate,
        vote_data: {}
      });

      setStatus({ type: 'success', message: response.data.message || 'Vote cast successfully!' });
      setVoterId('');
      setCandidate('');
      setStep(1);
      setCapturedImage(null);
      setBlinkCount(0);
      setBlinkDetected(false);
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
    setCapturedImage(null);
    setStatus({ type: '', message: '' });
    setBlinkCount(0);
    setBlinkDetected(false);
    if (blinkCheckInterval.current) {
      clearInterval(blinkCheckInterval.current);
    }
  };

  return (
    <div className="card">
      <h1>Cast Your Vote</h1>

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
              placeholder="Enter your voter ID"
              required
            />
          </div>

          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <button type="submit" disabled={!voterId}>
              Next: Face Verification
            </button>
          </div>
        </form>
      )}

      {step === 2 && (
        <div>
          <h2>Step 2: Face Verification</h2>
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
          <div style={{ textAlign: 'center', marginTop: '10px' }}>
            <button onClick={handleFaceVerification} disabled={isProcessing}>
              {isProcessing ? 'Verifying...' : 'Verify Face'}
            </button>
            <button onClick={() => setFacingMode(facingMode === 'user' ? 'environment' : 'user')}>
              Switch Camera
            </button>
            <button onClick={reset}>Reset</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div>
          <h2>Step 3: Liveness Detection</h2>
          <p style={{ marginBottom: '15px', color: '#666' }}>
            Please blink your eyes naturally. The system will detect your blink to ensure you are a real person.
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
          {blinkDetected && (
            <div className="status-message status-success">
              Blink detected! Verifying liveness...
            </div>
          )}
          <div style={{ textAlign: 'center', marginTop: '10px' }}>
            <button onClick={reset}>Reset</button>
          </div>
        </div>
      )}

      {step === 4 && (
        <form onSubmit={handleVote}>
          <h2>Step 4: Cast Your Vote</h2>
          <div className="form-group">
            <label>Select Candidate *</label>
            <div className="candidates-list">
              {candidates.length > 0 ? (
                candidates.map((cand) => (
                  <label key={cand.id} style={{ display: 'block', marginBottom: '10px', cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name="candidate"
                      value={cand.name}
                      checked={candidate === cand.name}
                      onChange={(e) => setCandidate(e.target.value)}
                      style={{ marginRight: '10px' }}
                    />
                    <strong>{cand.name}</strong> ({cand.party})
                  </label>
                ))
              ) : (
                <p>No candidates available. Please contact admin.</p>
              )}
            </div>
          </div>

          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <button type="submit" disabled={isProcessing || !candidate}>
              {isProcessing ? 'Casting Vote...' : 'Cast Vote'}
            </button>
            <button type="button" onClick={reset} className="secondary" style={{ marginLeft: '10px' }}>Reset</button>
          </div>
        </form>
      )}

      {status.message && (
        <div className={`status-message status-${status.type}`}>
          {status.message}
        </div>
      )}
    </div>
  );
}

export default Voting;
