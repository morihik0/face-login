import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token (if needed in future)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request was made but no response
      console.error('Network Error:', error.request);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// User API endpoints
export const userAPI = {
  // Get all users
  getAll: () => api.get('/users'),
  
  // Get user by ID
  getById: (id) => api.get(`/users/${id}`),
  
  // Create new user
  create: (userData) => api.post('/users', userData),
  
  // Update user
  update: (id, userData) => api.put(`/users/${id}`, userData),
  
  // Delete user
  delete: (id) => api.delete(`/users/${id}`),
};

// Face Recognition API endpoints
export const faceAPI = {
  // Register face for user
  register: (userId, imageBase64) => 
    api.post('/recognition/register', {
      user_id: userId,
      image: imageBase64,
    }),
  
  // Authenticate face
  authenticate: (imageBase64) =>
    api.post('/recognition/authenticate', {
      image: imageBase64,
    }),
  
  // Get authentication history
  getHistory: (params = {}) =>
    api.get('/recognition/history', { params }),
};

// Public API endpoints (no authentication required)
export const publicAPI = {
  // Register new user with face
  registerUserWithFace: (userData) =>
    axios.post('/api/public/register-user-with-face', userData),
  
  // Check email availability
  checkEmail: (email) =>
    axios.post('/api/public/check-email', { email }),
};

// Authentication API endpoints
export const authAPI = {
  // Login with face
  login: (imageBase64) =>
    axios.post('/api/auth/login', { image: imageBase64 }),
  
  // Refresh token
  refresh: (refreshToken) =>
    axios.post('/api/auth/refresh', {}, {
      headers: { Authorization: `Bearer ${refreshToken}` }
    }),
  
  // Get current user
  getCurrentUser: () => api.get('/auth/me'),
  
  // Logout
  logout: () => api.post('/auth/logout'),
};

// Convenience functions for the new signup flow
export const registerUserWithFace = (userData) => publicAPI.registerUserWithFace(userData);
export const checkEmailAvailability = (email) => publicAPI.checkEmail(email);

// Helper function to convert image to base64
export const imageToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      // Remove the data URL prefix to get just the base64 string
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = (error) => reject(error);
  });
};

// Helper function to capture image from webcam
export const captureWebcamImage = (webcamRef) => {
  if (webcamRef.current) {
    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      // Remove the data URL prefix to get just the base64 string
      return imageSrc.split(',')[1];
    }
  }
  return null;
};

export default api;