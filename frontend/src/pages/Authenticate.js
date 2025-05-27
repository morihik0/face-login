import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { faceAPI } from '../services/api';
import WebcamCapture from '../components/WebcamCapture';

const Authenticate = () => {
  const [capturedImage, setCapturedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [showWebcam, setShowWebcam] = useState(true);

  const handleImageCapture = (base64Image) => {
    setCapturedImage(base64Image);
    setShowWebcam(false);
    performAuthentication(base64Image);
  };

  const performAuthentication = async (base64Image) => {
    setLoading(true);
    setResult(null);

    try {
      const response = await faceAPI.authenticate(base64Image);
      const data = response.data.data;
      
      setResult({
        success: true,
        authenticated: data.authenticated,
        user: data.user,
        confidence: data.confidence
      });
    } catch (error) {
      console.error('Authentication error:', error);
      
      if (error.response?.status === 401) {
        setResult({
          success: false,
          authenticated: false,
          message: 'No matching face found in the system'
        });
      } else {
        setResult({
          success: false,
          authenticated: false,
          message: error.response?.data?.message || 'Authentication failed'
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const resetAuthentication = () => {
    setCapturedImage(null);
    setResult(null);
    setShowWebcam(true);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Face Authentication</h1>
        <Link
          to="/signup"
          className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 transition-colors"
        >
          新規アカウント作成
        </Link>
      </div>

      {/* Authentication Status */}
      {result && (
        <div className={`mb-6 p-6 rounded-lg ${
          result.authenticated 
            ? 'bg-green-50 border-2 border-green-500' 
            : 'bg-red-50 border-2 border-red-500'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`text-5xl ${
                result.authenticated ? 'text-green-600' : 'text-red-600'
              }`}>
                {result.authenticated ? '✅' : '❌'}
              </div>
              <div>
                <h2 className={`text-2xl font-bold ${
                  result.authenticated ? 'text-green-800' : 'text-red-800'
                }`}>
                  {result.authenticated ? 'Authentication Successful!' : 'Authentication Failed'}
                </h2>
                {result.authenticated && result.user && (
                  <div className="mt-2 text-green-700">
                    <p className="text-lg">Welcome, <strong>{result.user.name}</strong></p>
                    <p className="text-sm text-green-600">Email: {result.user.email}</p>
                    <p className="text-sm text-green-600">
                      Confidence: {(result.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                )}
                {!result.authenticated && (
                  <div className="mt-2 text-red-700">
                    <p>{result.message || 'Face not recognized'}</p>
                    <p className="text-sm mt-2">
                      アカウントをお持ちでない場合は、
                      <Link to="/signup" className="text-blue-600 hover:text-blue-800 underline ml-1">
                        こちらから新規登録
                      </Link>
                      してください。
                    </p>
                  </div>
                )}
              </div>
            </div>
            
            <button
              onClick={resetAuthentication}
              className="btn-outline"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="card text-center py-12">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Authenticating...</p>
          <p className="text-sm text-gray-500 mt-2">
            Comparing your face with registered users
          </p>
        </div>
      )}

      {/* Webcam Capture */}
      {showWebcam && !loading && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Capture Your Face</h2>
          <WebcamCapture onCapture={handleImageCapture} showPreview={false} />
        </div>
      )}

      {/* Captured Image Preview */}
      {capturedImage && !showWebcam && !loading && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Captured Photo</h2>
          <div className="max-w-md mx-auto">
            <img
              src={`data:image/jpeg;base64,${capturedImage}`}
              alt="Captured face"
              className="rounded-lg shadow-lg w-full"
            />
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-8 card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">How it works</h3>
        <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
          <li>Position your face clearly in the camera frame</li>
          <li>Click the capture button to take a photo</li>
          <li>The system will compare your face with all registered users</li>
          <li>If a match is found, you'll see the user details and confidence score</li>
          <li>The authentication threshold is set to ensure security</li>
        </ul>
      </div>

      {/* Recent Authentication Stats */}
      {result && result.authenticated && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card text-center">
            <div className="text-3xl mb-2">👤</div>
            <p className="text-sm text-gray-600">Authenticated User</p>
            <p className="font-semibold">{result.user.name}</p>
          </div>
          <div className="card text-center">
            <div className="text-3xl mb-2">🎯</div>
            <p className="text-sm text-gray-600">Confidence Score</p>
            <p className="font-semibold">{(result.confidence * 100).toFixed(1)}%</p>
          </div>
          <div className="card text-center">
            <div className="text-3xl mb-2">⏱️</div>
            <p className="text-sm text-gray-600">Authentication Time</p>
            <p className="font-semibold">{new Date().toLocaleTimeString()}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Authenticate;