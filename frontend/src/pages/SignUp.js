import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import WebcamCapture from '../components/WebcamCapture';
import { registerUserWithFace, checkEmailAvailability } from '../services/api';

const SignUp = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: ''
  });
  const [capturedImage, setCapturedImage] = useState(null);
  const [step, setStep] = useState(1); // 1: Form, 2: Camera, 3: Confirmation
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [emailChecking, setEmailChecking] = useState(false);
  const [emailAvailable, setEmailAvailable] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Reset email availability when email changes
    if (name === 'email') {
      setEmailAvailable(null);
    }
  };

  const checkEmail = async () => {
    if (!formData.email || !formData.email.includes('@')) {
      setError('有効なメールアドレスを入力してください');
      return;
    }

    setEmailChecking(true);
    setError('');

    try {
      const response = await checkEmailAvailability(formData.email);
      setEmailAvailable(response.data.available);
      
      if (!response.data.available) {
        setError('このメールアドレスは既に使用されています');
      }
    } catch (err) {
      setError('メールアドレスの確認に失敗しました');
    } finally {
      setEmailChecking(false);
    }
  };

  const handleNextStep = () => {
    if (!formData.name.trim()) {
      setError('名前を入力してください');
      return;
    }

    if (!formData.email.trim()) {
      setError('メールアドレスを入力してください');
      return;
    }

    if (emailAvailable === false) {
      setError('このメールアドレスは既に使用されています');
      return;
    }

    if (emailAvailable === null) {
      setError('メールアドレスの確認を行ってください');
      return;
    }

    setError('');
    setStep(2);
  };

  const handleImageCapture = (imageData) => {
    setCapturedImage(imageData);
    setStep(3);
  };

  const handleRetakePhoto = () => {
    setCapturedImage(null);
    setStep(2);
  };

  const handleSubmit = async () => {
    if (!capturedImage) {
      setError('顔写真を撮影してください');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await registerUserWithFace({
        name: formData.name,
        email: formData.email,
        image: capturedImage.split(',')[1] // Remove data:image/jpeg;base64, prefix
      });

      // Store tokens for immediate login
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));

      // Redirect to dashboard
      navigate('/dashboard', { 
        state: { 
          message: 'アカウントが正常に作成されました！',
          user: response.data.user 
        }
      });

    } catch (err) {
      setError(err.response?.data?.message || '登録に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const renderStep1 = () => (
    <div className="max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-center mb-6">新規アカウント作成</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            名前
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="お名前を入力してください"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            メールアドレス
          </label>
          <div className="flex space-x-2">
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="email@example.com"
              required
            />
            <button
              type="button"
              onClick={checkEmail}
              disabled={emailChecking || !formData.email}
              className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 disabled:opacity-50"
            >
              {emailChecking ? '確認中...' : '確認'}
            </button>
          </div>
          
          {emailAvailable === true && (
            <p className="text-green-600 text-sm mt-1">✓ このメールアドレスは使用可能です</p>
          )}
          {emailAvailable === false && (
            <p className="text-red-600 text-sm mt-1">✗ このメールアドレスは既に使用されています</p>
          )}
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <button
          type="button"
          onClick={handleNextStep}
          disabled={!formData.name || !formData.email || emailAvailable !== true}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          次へ（顔写真撮影）
        </button>

        <div className="text-center">
          <button
            type="button"
            onClick={() => navigate('/authenticate')}
            className="text-blue-500 hover:text-blue-700 text-sm"
          >
            既にアカウントをお持ちの方はこちら
          </button>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-center mb-6">顔写真を撮影</h2>
      
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-800 mb-2">撮影のコツ</h3>
        <ul className="text-blue-700 text-sm space-y-1">
          <li>• 明るい場所で撮影してください</li>
          <li>• カメラを正面から見てください</li>
          <li>• 顔全体がフレームに入るようにしてください</li>
          <li>• 眼鏡やマスクは外してください</li>
        </ul>
      </div>

      <WebcamCapture
        onCapture={handleImageCapture}
        showPreview={true}
        captureButtonText="この写真で登録"
        retakeButtonText="撮り直し"
      />

      <div className="text-center mt-6">
        <button
          type="button"
          onClick={() => setStep(1)}
          className="text-gray-500 hover:text-gray-700"
        >
          ← 前に戻る
        </button>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-center mb-6">登録内容の確認</h2>
      
      <div className="space-y-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">アカウント情報</h3>
          <p><strong>名前:</strong> {formData.name}</p>
          <p><strong>メール:</strong> {formData.email}</p>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">顔写真</h3>
          {capturedImage && (
            <img
              src={capturedImage}
              alt="Captured face"
              className="w-32 h-32 object-cover rounded-lg mx-auto"
            />
          )}
          <button
            type="button"
            onClick={handleRetakePhoto}
            className="text-blue-500 hover:text-blue-700 text-sm mt-2 block mx-auto"
          >
            写真を撮り直す
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="flex space-x-4">
          <button
            type="button"
            onClick={() => setStep(2)}
            className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600"
          >
            戻る
          </button>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading}
            className="flex-1 bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 disabled:opacity-50"
          >
            {loading ? '登録中...' : 'アカウント作成'}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex justify-center space-x-4">
            {[1, 2, 3].map((stepNumber) => (
              <div
                key={stepNumber}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                  step >= stepNumber
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}
              >
                {stepNumber}
              </div>
            ))}
          </div>
          <div className="flex justify-center space-x-8 mt-2">
            <span className={`text-sm ${step >= 1 ? 'text-blue-500' : 'text-gray-500'}`}>
              基本情報
            </span>
            <span className={`text-sm ${step >= 2 ? 'text-blue-500' : 'text-gray-500'}`}>
              顔写真
            </span>
            <span className={`text-sm ${step >= 3 ? 'text-blue-500' : 'text-gray-500'}`}>
              確認
            </span>
          </div>
        </div>

        {/* Step content */}
        <div className="bg-white rounded-lg shadow-md p-8">
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
        </div>
      </div>
    </div>
  );
};

export default SignUp;