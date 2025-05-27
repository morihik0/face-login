import React, { useState, useEffect } from 'react';
import { userAPI, faceAPI } from '../services/api';
import WebcamCapture from '../components/WebcamCapture';

const Register = () => {
  const [users, setUsers] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [capturedImage, setCapturedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [registrationStep, setRegistrationStep] = useState(1);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await userAPI.getAll();
      setUsers(response.data.data.users);
    } catch (error) {
      console.error('Error fetching users:', error);
      setMessage({ type: 'error', text: 'Failed to fetch users' });
    }
  };

  const handleImageCapture = (base64Image) => {
    setCapturedImage(base64Image);
    setRegistrationStep(3);
  };

  const handleRegister = async () => {
    if (!selectedUserId || !capturedImage) {
      setMessage({ type: 'error', text: 'Please select a user and capture an image' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await faceAPI.register(parseInt(selectedUserId), capturedImage);
      const data = response.data.data;
      
      setMessage({
        type: 'success',
        text: `Face registered successfully! User now has ${data.face_count} registered face(s).`
      });
      
      // Reset form
      setTimeout(() => {
        setSelectedUserId('');
        setCapturedImage(null);
        setRegistrationStep(1);
        setMessage({ type: '', text: '' });
      }, 3000);
    } catch (error) {
      console.error('Registration error:', error);
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'Failed to register face'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUserSelect = (e) => {
    setSelectedUserId(e.target.value);
    if (e.target.value) {
      setRegistrationStep(2);
    }
  };

  const resetProcess = () => {
    setSelectedUserId('');
    setCapturedImage(null);
    setRegistrationStep(1);
    setMessage({ type: '', text: '' });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Register Face</h1>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className={`flex items-center ${registrationStep >= 1 ? 'text-primary-600' : 'text-gray-400'}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              registrationStep >= 1 ? 'bg-primary-600 text-white' : 'bg-gray-300'
            }`}>
              1
            </div>
            <span className="ml-2 font-medium">Select User</span>
          </div>
          
          <div className={`flex-1 h-1 mx-4 ${
            registrationStep >= 2 ? 'bg-primary-600' : 'bg-gray-300'
          }`}></div>
          
          <div className={`flex items-center ${registrationStep >= 2 ? 'text-primary-600' : 'text-gray-400'}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              registrationStep >= 2 ? 'bg-primary-600 text-white' : 'bg-gray-300'
            }`}>
              2
            </div>
            <span className="ml-2 font-medium">Capture Face</span>
          </div>
          
          <div className={`flex-1 h-1 mx-4 ${
            registrationStep >= 3 ? 'bg-primary-600' : 'bg-gray-300'
          }`}></div>
          
          <div className={`flex items-center ${registrationStep >= 3 ? 'text-primary-600' : 'text-gray-400'}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              registrationStep >= 3 ? 'bg-primary-600 text-white' : 'bg-gray-300'
            }`}>
              3
            </div>
            <span className="ml-2 font-medium">Confirm & Register</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      {message.text && (
        <div className={`mb-6 ${
          message.type === 'success' ? 'alert-success' : 'alert-error'
        }`}>
          {message.text}
        </div>
      )}

      {/* Step 1: User Selection */}
      {registrationStep >= 1 && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">Step 1: Select User</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select a user to register face for:
              </label>
              <select
                value={selectedUserId}
                onChange={handleUserSelect}
                className="input-field"
                disabled={registrationStep > 1}
              >
                <option value="">-- Select a user --</option>
                {users.map(user => (
                  <option key={user.id} value={user.id}>
                    {user.name} ({user.email})
                  </option>
                ))}
              </select>
            </div>
            
            {selectedUserId && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-blue-800">
                  Selected: <strong>{users.find(u => u.id === parseInt(selectedUserId))?.name}</strong>
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Step 2: Capture Face */}
      {registrationStep >= 2 && !capturedImage && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">Step 2: Capture Face Photo</h2>
          <WebcamCapture onCapture={handleImageCapture} showPreview={false} />
        </div>
      )}

      {/* Step 3: Confirm and Register */}
      {registrationStep >= 3 && capturedImage && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">Step 3: Confirm and Register</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-gray-700 mb-2">User Information</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                {users.find(u => u.id === parseInt(selectedUserId)) && (
                  <>
                    <p><strong>Name:</strong> {users.find(u => u.id === parseInt(selectedUserId)).name}</p>
                    <p><strong>Email:</strong> {users.find(u => u.id === parseInt(selectedUserId)).email}</p>
                  </>
                )}
              </div>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-700 mb-2">Captured Photo</h3>
              <img
                src={`data:image/jpeg;base64,${capturedImage}`}
                alt="Captured face"
                className="rounded-lg shadow-md w-full"
              />
            </div>
          </div>

          <div className="mt-6 flex justify-end space-x-4">
            <button
              onClick={resetProcess}
              className="btn-outline"
              disabled={loading}
            >
              Start Over
            </button>
            <button
              onClick={handleRegister}
              className="btn-primary"
              disabled={loading}
            >
              {loading ? 'Registering...' : 'Register Face'}
            </button>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">Instructions</h3>
        <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
          <li>Select a user from the dropdown to register their face</li>
          <li>Position your face clearly in the camera frame</li>
          <li>Ensure good lighting and avoid shadows on your face</li>
          <li>Look directly at the camera when capturing</li>
          <li>Each user can register up to 5 different face images</li>
        </ul>
      </div>
    </div>
  );
};

export default Register;