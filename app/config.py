"""
Configuration settings for the Face Login application.
"""
import os
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent

# Database settings
DATABASE = {
    'path': os.environ.get('DB_PATH', os.path.join(BASE_DIR, 'face_login.db')),
}

# Face recognition settings
FACE_RECOGNITION = {
    'threshold': float(os.environ.get('FACE_RECOGNITION_THRESHOLD', 0.6)),
    'max_faces_per_user': int(os.environ.get('MAX_FACES_PER_USER', 5)),
}

# Storage settings
STORAGE = {
    'face_images_dir': os.environ.get('FACE_IMAGES_DIR', os.path.join(BASE_DIR, 'face_images')),
}

# API settings
API = {
    'cors_origins': os.environ.get('CORS_ORIGINS', '*').split(','),
}

# Logging settings
LOGGING = {
    'level': os.environ.get('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.environ.get('LOG_FILE', os.path.join(BASE_DIR, 'face_login.log')),
}