# Face Login System 🔐

A modern web-based facial recognition authentication system built with Flask (backend) and React (frontend). The system provides secure user authentication using face recognition technology with a user-friendly interface.

## 🌟 Features

- **User Management**: Create, update, and delete user accounts
- **Face Registration**: Register multiple face images per user (up to 5)
- **Face Authentication**: Authenticate users using facial recognition
- **Real-time Webcam**: Capture face images directly from webcam
- **Authentication History**: Track and export authentication logs
- **Dashboard**: View system statistics and recent activity
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

```
FaceLogin/
├── app/                       # Backend Flask application
│   ├── api/                   # API routes
│   ├── database/              # Database models and connection
│   └── services/              # Business logic services
├── frontend/                  # React frontend application
│   ├── public/                # Static files
│   ├── src/                   # React components and pages
│   └── package.json          # Frontend dependencies
├── tests/                     # Unit tests
├── test_tools/               # Testing and analysis tools
│   ├── test_*.py             # API and system tests
│   ├── analyze_*.py          # Performance analysis
│   ├── generate_*.py         # Test data generation
│   └── test_browser.html     # Browser-based testing
├── docs/                     # Documentation
│   ├── implementation_plan.md
│   ├── DOCKER_GUIDE.md
│   ├── SECURITY_IMPLEMENTATION.md
│   └── other documentation files
├── face_images/              # Stored face images
├── docker-compose.yml        # Docker configuration
└── run.py                    # Backend entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Node.js 14+
- Webcam (for face capture features)

### Option 1: Using the Start Script (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd FaceLogin

# Run the start script
./start_system.sh
```

The script will:
- Install all dependencies
- Start the backend API on http://localhost:5001
- Start the frontend UI on http://localhost:3000
- Open your browser automatically

Press `Ctrl+C` to stop all services.

### Option 2: Manual Setup

#### Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask API
python3 run.py
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the React app
npm start
```

## 📖 Usage Guide

### 1. User Registration
- Navigate to "Users" page
- Click "Add New User"
- Enter name and email
- Click "Add User"

### 2. Face Registration
- Go to "Register Face" page
- Select a user from dropdown
- Position face in camera frame
- Click "Capture Photo"
- Confirm and register

### 3. Face Authentication
- Go to "Authenticate" page
- Position face in camera
- Click "Capture Photo"
- System will identify you

### 4. View History
- Go to "History" page
- Filter by user or date
- Export data as CSV

## 🔧 Configuration

### Backend Configuration (`app/config.py`)

```python
# Face recognition settings
FACE_RECOGNITION = {
    'threshold': 0.6,          # Authentication threshold
    'max_faces_per_user': 5    # Max faces per user
}
```

### Frontend Configuration

Create `.env` file in frontend directory:

```env
REACT_APP_API_URL=http://localhost:5001
```

## 📊 API Documentation

### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | Get all users |
| GET | `/api/users/{id}` | Get user by ID |
| POST | `/api/users` | Create new user |
| PUT | `/api/users/{id}` | Update user |
| DELETE | `/api/users/{id}` | Delete user |

### Face Recognition

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recognition/register` | Register face for user |
| POST | `/api/recognition/authenticate` | Authenticate face |
| GET | `/api/recognition/history` | Get authentication logs |

## 🧪 Testing

### Run Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_face_detection.py
```

### Test Coverage Areas

- Face detection accuracy
- Authentication accuracy
- API endpoints
- Database operations
- Performance metrics

## 📈 Performance

- **Face Detection**: ~50-100ms
- **Face Encoding**: ~100-200ms
- **Authentication**: ~200-300ms total
- **Detection Rate**: 95%+
- **Authentication Accuracy**: 98%+

## 🔒 Security Considerations

- Single face validation for registration
- Configurable authentication threshold
- Authentication logging for audit trails
- Face images stored with unique filenames
- Input validation on all endpoints

## 🐛 Troubleshooting

### Common Issues

1. **Camera not working**
   - Check browser permissions
   - Ensure HTTPS or localhost
   - Try different browser

2. **API connection error**
   - Verify backend is running on port 5001
   - Check CORS settings
   - Verify proxy configuration

3. **Face not detected**
   - Ensure good lighting
   - Face camera directly
   - Remove glasses/masks if needed

## 🧪 Testing Tools

The `test_tools/` directory contains comprehensive testing and analysis tools:

### API Testing
- `test_api_endpoints.py` - Complete API endpoint testing
- `test_api_simple.py` - Basic API functionality tests
- `test_full_system.py` - End-to-end system testing
- `test_jwt_auth.py` - JWT authentication testing
- `test_browser.html` - Browser-based interactive testing

### Performance Analysis
- `analyze_face_detection_rate.py` - Face detection accuracy analysis
- `analyze_false_authentication_rate.py` - Authentication error analysis
- `measure_performance.py` - System performance benchmarking
- `optimize_face_recognition.py` - Performance optimization tools

### Test Data Generation
- `generate_test_images.py` - Generate test face images
- `generate_expression_images.py` - Create expression variations
- `generate_occlusion_images.py` - Create occlusion test cases
- `generate_background_images.py` - Generate background variations

### Visualization
- `visualize_test_results.py` - Create performance charts
- `test_results_visualization.png` - Visual test results
- `api_test_results.png` - API testing results

## 📚 Documentation

The `docs/` directory contains detailed documentation:

### Implementation Guides
- `implementation_plan.md` - Original implementation plan
- `face_detection_service_plan.md` - Face detection service design
- `face_recognition_libraries_plan.md` - Library selection rationale

### System Documentation
- `FINAL_PROJECT_SUMMARY.md` - Complete project overview
- `PROJECT_STATUS.md` - Current system status
- `SECURITY_IMPLEMENTATION.md` - Security features and considerations
- `TEST_SUMMARY.md` - Testing methodology and results

### Setup Guides
- `DOCKER_GUIDE.md` - Docker deployment instructions
- `api_implementation_report.md` - API implementation details
- `task_list.md` - Development task tracking

## 🚀 Usage Examples

### Running Tests
```bash
# Run all API tests
python test_tools/test_api_endpoints.py

# Analyze face detection performance
python test_tools/analyze_face_detection_rate.py

# Generate test data
python test_tools/generate_test_images.py

# Visualize results
python test_tools/visualize_test_results.py
```

### Browser Testing
Open `test_tools/test_browser.html` in your browser for interactive testing of all API endpoints with a user-friendly interface.
   - Remove obstructions

4. **Low authentication confidence**
   - Re-register with better photos
   - Adjust threshold in config
   - Ensure consistent lighting

## 🚧 Known Limitations

- SQLite database (not for production scale)
- No API authentication (add JWT for production)
- Face images stored unencrypted
- Limited to 5 faces per user
- Best performance in Chrome/Edge

## 🔮 Future Enhancements

- [ ] Docker containerization
- [ ] JWT authentication
- [ ] Rate limiting
- [ ] Image encryption
- [ ] Admin dashboard
- [ ] Email notifications
- [ ] Multi-factor authentication
- [ ] PostgreSQL support

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For issues and questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review test files for usage examples
- Open an issue on GitHub

---

Built with ❤️ using Flask, React, and face_recognition