"""
Public API routes that don't require authentication.
"""
import base64
import cv2
import numpy as np
from flask import jsonify, request
from app.api import public_bp
from app.database.models import User
from app.services.face_recognition import register_face
from app.services.auth import AuthService
import logging

# Configure logger
logger = logging.getLogger(__name__)

@public_bp.route('/register-user-with-face', methods=['POST'])
def register_user_with_face():
    """
    Register a new user with face data (no authentication required).
    
    Expected JSON payload:
    {
        "name": "User Name",
        "email": "user@example.com",
        "image": "base64_encoded_image_data"
    }
    
    Returns:
        JSON: User information and JWT tokens for immediate login.
    """
    logger.info("Public user registration with face request")
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided",
                "data": None
            }), 400
        
        # Validate required fields
        name = data.get('name')
        email = data.get('email')
        image_data = data.get('image')
        
        if not all([name, email, image_data]):
            return jsonify({
                "status": "error",
                "message": "name, email, and image are required",
                "data": None
            }), 400
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({
                "status": "error",
                "message": "Invalid email format",
                "data": None
            }), 400
        
        # Check if email already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            return jsonify({
                "status": "error",
                "message": "User with this email already exists",
                "data": None
            }), 409
        
        # Decode and validate image
        try:
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
                
        except Exception as e:
            logger.error(f"Error decoding image: {e}")
            return jsonify({
                "status": "error",
                "message": "Invalid image data",
                "data": None
            }), 400
        
        # Create new user
        try:
            user = User.create(name=name, email=email)
            if user is None:
                raise ValueError("Failed to create user - user object is None")
            logger.info(f"Created new user: {user.id}")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return jsonify({
                "status": "error",
                "message": "Failed to create user",
                "error": str(e)
            }), 500
        
        # Register face for the new user
        try:
            face_encoding_obj = register_face(user.id, image)
            logger.info(f"Face registered successfully for user {user.id}")
            
        except Exception as e:
            # If face registration fails, delete the created user
            try:
                User.delete(user.id)
                logger.info(f"Deleted user {user.id} due to face registration failure")
            except Exception as delete_error:
                logger.error(f"Error deleting user after face registration failure: {delete_error}")
            
            logger.error(f"Error registering face: {e}")
            return jsonify({
                "status": "error",
                "message": "Failed to register face",
                "error": str(e)
            }), 400
        
        # Generate JWT tokens for immediate login
        tokens = AuthService.generate_tokens(user.id)
        
        return jsonify({
            "status": "success",
            "message": "User registered successfully with face authentication",
            "data": {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at,
                    "is_active": user.is_active
                },
                "face_registration": {
                    "image_path": face_encoding_obj.image_path,
                    "face_count": 1
                },
                **tokens
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error during user registration: {e}")
        return jsonify({
            "status": "error",
            "message": "Registration failed",
            "error": str(e)
        }), 500

@public_bp.route('/check-email', methods=['POST'])
def check_email():
    """
    Check if an email is already registered.
    
    Expected JSON payload:
    {
        "email": "user@example.com"
    }
    
    Returns:
        JSON: Email availability status.
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({
                "status": "error",
                "message": "Email is required",
                "data": None
            }), 400
        
        email = data.get('email')
        existing_user = User.get_by_email(email)
        
        return jsonify({
            "status": "success",
            "message": "Email check completed",
            "data": {
                "email": email,
                "available": existing_user is None
            }
        })
        
    except Exception as e:
        logger.error(f"Error checking email: {e}")
        return jsonify({
            "status": "error",
            "message": "Email check failed",
            "error": str(e)
        }), 500