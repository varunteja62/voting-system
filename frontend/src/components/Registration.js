import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
// import FingerprintScanner from './FingerprintScanner';

const API_BASE_URL = 'http://localhost:5000/api';

function Registration() {
  const [voterId, setVoterId] = useState('');
  const [name, setName] = useState('');
  // const [fingerprint, setFingerprint] = useState('');
  const [capturedImage, setCapturedImage] = useState(null);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isProcessing, setIsProcessing] = useState(false);

  const webcamRef = useRef(null);
  const [facingMode, setFacingMode] = useState('user');

  // Liveness State
  const [livenessStep, setLivenessStep] = useState(0); // 0: Left, 1: Right, 2: Center/Ready
  const [currentPose, setCurrentPose] = useState('');
  const checkInterval = useRef(null);

  useEffect(() => {
    startLivenessCheck();
    return () => {
      if (checkInterval.current) clearInterval(checkInterval.current);
    };
  }, [livenessStep]);

  const startLivenessCheck = () => {
    if (checkInterval.current) clearInterval(checkInterval.current);

    checkInterval.current = setInterval(async () => {
      if (capturedImage) return; // Stop checking if image is captured

      const imageSrc = webcamRef.current?.getScreenshot();
      if (!imageSrc) return;

      try {
        const response = await axios.post(`${API_BASE_URL}/check_head_pose`, {
          face_image: imageSrc
        });

        const pose = response.data.pose;
        console.log("Current Pose:", pose, "Step:", livenessStep);
        setCurrentPose(pose);

        if (livenessStep === 0 && pose === 'Left') {
          setStatus({ type: 'success', message: 'Left Turn Verified!' });
          setLivenessStep(1);
        } else if (livenessStep === 1 && pose === 'Right') {
          setStatus({ type: 'success', message: 'Right Turn Verified!' });
          setLivenessStep(2);
        } else if (livenessStep === 2 && pose === 'Center') {
          setStatus({ type: 'success', message: 'Liveness Verified! You can now capture.' });
        }

      } catch (error) {
        console.error("Pose check error", error);
      }
    }, 1000); // Check every 1 second
  };

  // const handleFingerprintScan = (fingerprintData) => {
  //   setFingerprint(fingerprintData);
  //   setStatus({ type: 'success', message: 'Fingerprint captured successfully!' });
  // };

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setCapturedImage(imageSrc);
      setStatus({ type: 'info', message: 'Image captured. Please verify and submit.' });
    }
  }, [webcamRef]);

  const retake = () => {
    setCapturedImage(null);
    setStatus({ type: '', message: '' });
    setLivenessStep(0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!capturedImage) {
      setStatus({ type: 'error', message: 'Please capture your face image first' });
      return;
    }

    if (!voterId || !name) {
      setStatus({ type: 'error', message: 'Please fill in all fields' });
      return;
    }

    setIsProcessing(true);
    setStatus({ type: 'info', message: 'Registering voter...' });

    try {
      const response = await axios.post(`${API_BASE_URL}/register`, {
        voter_id: voterId,
        name: name,
        face_image: capturedImage,
      });

      setStatus({ type: 'success', message: response.data.message || 'Registration successful!' });
      setVoterId('');
      setName('');
      setCapturedImage(null);
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.response?.data?.error || 'Registration failed. Please try again.'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="card">
      <h1>Voter Registration</h1>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="voterId">Voter ID *</label>
          <input
            type="text"
            id="voterId"
            value={voterId}
            onChange={(e) => setVoterId(e.target.value)}
            placeholder="Enter unique voter ID"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="name">Full Name *</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your full name"
            required
          />
        </div>

        {/*     <FingerprintScanner 
          onScan={handleFingerprintScan} 
          disabled={isProcessing}
        /> */}


        <div className="form-group">
          <label>Face Capture *</label>
          <div className="video-container">
            {!capturedImage ? (
              <>
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

                {/* Liveness Instructions Overlay */}
                <div style={{
                  position: 'absolute',
                  top: '10px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  backgroundColor: 'rgba(0,0,0,0.7)',
                  color: 'white',
                  padding: '10px',
                  borderRadius: '5px',
                  zIndex: 10
                }}>
                  {livenessStep === 0 && "Step 1: Turn Head LEFT"}
                  {livenessStep === 1 && "Step 2: Turn Head RIGHT"}
                  {livenessStep === 2 && "Step 3: Look Center & Capture"}
                  <div style={{ fontSize: '0.8em', marginTop: '5px', color: '#aaa' }}>
                    (Detected: {currentPose || "Waiting..."})
                  </div>
                </div>

                <div style={{ textAlign: 'center', marginTop: '10px' }}>
                  {livenessStep === 2 ? (
                    <button type="button" onClick={capture}>
                      Capture & Finish
                    </button>
                  ) : (
                    <div style={{ color: 'orange' }}>
                      Please follow instructions to verify liveness
                    </div>
                  )}

                  <button
                    type="button"
                    onClick={() => setFacingMode(facingMode === 'user' ? 'environment' : 'user')}
                    style={{ marginLeft: '10px' }}
                  >
                    Switch Camera
                  </button>
                </div>
              </>
            ) : (
              <>
                <img src={capturedImage} alt="Captured" style={{ width: '100%' }} />
                <div style={{ textAlign: 'center', marginTop: '10px' }}>
                  <button type="button" onClick={retake}>
                    Retake
                  </button>
                </div>
              </>
            )}
          </div>
          <small style={{ color: '#666', fontSize: '12px', display: 'block', marginTop: '5px' }}>
            Ensure only one person is visible in the frame
          </small>
        </div>

        {status.message && (
          <div className={`status-message status-${status.type}`}>
            {status.message}
          </div>
        )}

        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <button type="submit" disabled={isProcessing}>
            {isProcessing ? 'Registering...' : 'Register Voter'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default Registration;

