import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
// import FingerprintScanner from './FingerprintScanner';

import API_BASE_URL from '../apiConfig';

function Registration() {
  const [voterId, setVoterId] = useState('');
  const [name, setName] = useState('');
  const [capturedImages, setCapturedImages] = useState({ left: null, right: null, center: null });
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isProcessing, setIsProcessing] = useState(false);

  const webcamRef = useRef(null);
  const [facingMode, setFacingMode] = useState('user');

  const [livenessStep, setLivenessStep] = useState(0); // 0: Left, 1: Right, 2: Center/Ready
  const [currentPose, setCurrentPose] = useState('');
  const checkInterval = useRef(null);

  const startLivenessCheck = useCallback(() => {
    if (checkInterval.current) clearInterval(checkInterval.current);

    checkInterval.current = setInterval(async () => {
      // Don't check if all images are captured
      if (capturedImages.left && capturedImages.right && capturedImages.center) return;

      const imageSrc = webcamRef.current?.getScreenshot();
      if (!imageSrc) return;

      try {
        const response = await axios.post(`${API_BASE_URL}/check_head_pose`, {
          face_image: imageSrc
        });

        const pose = response.data.pose;
        setCurrentPose(pose);

        if (livenessStep === 0 && pose === 'Left') {
          setCapturedImages(prev => ({ ...prev, left: imageSrc }));
          setStatus({ type: 'success', message: 'Left Turn Captured! Now turn Right.' });
          setLivenessStep(1);
        } else if (livenessStep === 1 && pose === 'Right') {
          setCapturedImages(prev => ({ ...prev, right: imageSrc }));
          setStatus({ type: 'success', message: 'Right Turn Captured! Now look Center & click Capture.' });
          setLivenessStep(2);
        } else if (livenessStep === 2 && pose === 'Center') {
          // Just update status, wait for user to click capture
          setStatus({ type: 'success', message: 'Face Center! You can now click Capture.' });
        }

      } catch (error) {
        console.error("Pose check error", error);
        if (error.response?.data?.error) {
            setStatus({ type: 'error', message: `Detection Error: ${error.response.data.error}` });
            setCurrentPose("Error");
        } else {
            setCurrentPose("Network Error");
        }
      }
    }, 1000); // Check every 1 second
  }, [livenessStep, capturedImages]);

  useEffect(() => {
    startLivenessCheck();
    return () => {
      if (checkInterval.current) clearInterval(checkInterval.current);
    };
  }, [startLivenessCheck]);

  // const handleFingerprintScan = (fingerprintData) => {
  //   setFingerprint(fingerprintData);
  //   setStatus({ type: 'success', message: 'Fingerprint captured successfully!' });
  // };

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setCapturedImages(prev => ({ ...prev, center: imageSrc }));
      setStatus({ type: 'info', message: 'All angles captured. Please verify and submit.' });
    }
  }, [webcamRef]);

  const retake = () => {
    setCapturedImages({ left: null, right: null, center: null });
    setStatus({ type: '', message: '' });
    setLivenessStep(0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!capturedImages.left || !capturedImages.right || !capturedImages.center) {
      setStatus({ type: 'error', message: 'Please complete all pose captures first' });
      return;
    }

    if (!voterId || !name) {
      setStatus({ type: 'error', message: 'Please fill in all fields' });
      return;
    }

    setIsProcessing(true);
    setStatus({ type: 'info', message: 'Registering voter and processing multi-angle biometrics...' });

    try {
      const response = await axios.post(`${API_BASE_URL}/register`, {
        voter_id: voterId,
        name: name,
        face_images: [capturedImages.left, capturedImages.right, capturedImages.center],
      });

      setStatus({ type: 'success', message: response.data.message || 'Registration successful!' });
      setVoterId('');
      setName('');
      setCapturedImages({ left: null, right: null, center: null });
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
            {!capturedImages.center ? (
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
                  {livenessStep === 0 && "Step 1: Turn Head LEFT for side profile"}
                  {livenessStep === 1 && "Step 2: Turn Head RIGHT for side profile"}
                  {livenessStep === 2 && "Step 3: Look CENTER & Capture"}
                  <div style={{ fontSize: '0.8em', marginTop: '5px', color: '#aaa' }}>
                    (Detected: {currentPose || "Waiting..."})
                  </div>
                </div>

                <div style={{ textAlign: 'center', marginTop: '10px' }}>
                  {livenessStep === 2 ? (
                    <button type="button" onClick={capture}>
                      Capture Center & Finish
                    </button>
                  ) : (
                    <div style={{ color: 'orange', padding: '10px' }}>
                      Please follow on-screen instructions to verify liveness
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
                <img src={capturedImages.center} alt="Captured" style={{ width: '100%' }} />
                <div style={{ textAlign: 'center', marginTop: '10px' }}>
                  <button type="button" onClick={retake}>
                    Retake All Angles
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

