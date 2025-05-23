# Face Login System

A local face recognition authentication system that allows users to register their faces and authenticate in real-time.

## Project Overview

This application provides a secure and user-friendly face authentication system that can be run locally. It uses computer vision and machine learning techniques to detect and recognize faces.

## Features

- User registration with face recognition
- Real-time face authentication
- Authentication history tracking
- User management
- Secure face data storage

## Technology Stack

### Backend
- Python 3.9+
- Flask
- OpenCV
- face_recognition
- SQLite
- NumPy

### Frontend (Coming Soon)
- React.js
- Tailwind CSS
- Axios

### Infrastructure
- Docker (Coming Soon)

## Project Structure

```
face_login/
├── app/                    # Main application package
│   ├── api/                # API endpoints
│   ├── database/           # Database models and connection
│   ├── services/           # Face detection and recognition services
│   └── config.py           # Application configuration
├── tests/                  # Test modules
├── face_images/            # Storage for face images (created at runtime)
├── run.py                  # Application entry point
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd face-login
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python run.py
   ```

## Database Schema

The application uses SQLite with the following schema:

- **users**: Stores user information
  - id (INTEGER, PRIMARY KEY)
  - name (TEXT)
  - email (TEXT, UNIQUE)
  - created_at (TIMESTAMP)
  - is_active (BOOLEAN)

- **face_encodings**: Stores face recognition data
  - id (INTEGER, PRIMARY KEY)
  - user_id (INTEGER, FOREIGN KEY)
  - encoding (BLOB)
  - image_path (TEXT)
  - created_at (TIMESTAMP)

- **auth_logs**: Stores authentication history
  - id (INTEGER, PRIMARY KEY)
  - user_id (INTEGER, FOREIGN KEY)
  - success (BOOLEAN)
  - confidence (REAL)
  - timestamp (TIMESTAMP)

## Testing

Run the database tests:
```
python tests/test_database.py
```

## License

[MIT License](LICENSE)