import React, { useRef, useCallback, useState } from 'react';
import Webcam from 'react-webcam';

const WebcamCapture = ({ onCapture, showPreview = true }) => {
  const webcamRef = useRef(null);
  const [imgSrc, setImgSrc] = useState(null);
  const [facingMode, setFacingMode] = useState('user');

  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: facingMode
  };

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      setImgSrc(imageSrc);
      // Extract base64 data (remove data URL prefix)
      const base64 = imageSrc.split(',')[1];
      onCapture(base64);
    }
  }, [webcamRef, onCapture]);

  const retake = () => {
    setImgSrc(null);
  };

  const toggleCamera = () => {
    setFacingMode(prevMode => prevMode === 'user' ? 'environment' : 'user');
  };

  return (
    <div className="webcam-capture">
      {!imgSrc ? (
        <div className="space-y-4">
          <div className="relative">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              className="rounded-lg shadow-lg w-full"
            />
            
            {/* Face detection overlay */}
            <div className="absolute inset-0 pointer-events-none">
              <div className="w-full h-full flex items-center justify-center">
                <div className="w-64 h-80 border-2 border-primary-500 rounded-lg opacity-50"></div>
              </div>
            </div>

            {/* Camera controls */}
            <button
              onClick={toggleCamera}
              className="absolute top-4 right-4 bg-white bg-opacity-80 p-2 rounded-full shadow-lg hover:bg-opacity-100 transition-all"
              title="Switch camera"
            >
              🔄
            </button>
          </div>

          <div className="flex justify-center">
            <button
              onClick={capture}
              className="btn-primary flex items-center space-x-2"
            >
              <span>📸</span>
              <span>Capture Photo</span>
            </button>
          </div>

          <div className="text-center text-sm text-gray-600">
            Position your face within the frame and click capture
          </div>
        </div>
      ) : (
        showPreview && (
          <div className="space-y-4">
            <div className="relative">
              <img
                src={imgSrc}
                alt="Captured"
                className="rounded-lg shadow-lg w-full"
              />
            </div>

            <div className="flex justify-center space-x-4">
              <button
                onClick={retake}
                className="btn-outline flex items-center space-x-2"
              >
                <span>🔄</span>
                <span>Retake</span>
              </button>
            </div>

            <div className="text-center text-sm text-green-600">
              ✅ Photo captured successfully
            </div>
          </div>
        )
      )}
    </div>
  );
};

export default WebcamCapture;