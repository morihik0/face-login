"""
Authentication API routes.
"""
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import auth_bp
from app.services.auth import AuthService
from app.services.face_recognition import authenticate_face
from app.database.models import User
from app.utils import create_error_response, create_success_response, validate_request_data
import cv2
import numpy as np
import base64
import logging

# Configure logger
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user with face recognition and return JWT tokens.
    
    Expected JSON payload:
    {
        "image": "base64_encoded_image_data"
    }
    
    Returns:
        JSON: JWT tokens and user information.
    """
    logger.info("Face authentication login request")
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data or not data.get('image'):
            return jsonify({
                "status": "error",
                "message": "Image data is required",
                "data": None
            }), 400
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(data['image'])
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
        
        # Authenticate face
        success, user_id, confidence = authenticate_face(image)
        
        if not success:
            return jsonify({
                "status": "error",
                "message": "Face authentication failed",
                "data": None
            }), 401
        
        # Get user details
        user = User.get_by_id(user_id)
        if not user or not user.is_active:
            return jsonify({
                "status": "error",
                "message": "User account is not active",
                "data": None
            }), 401
        
        # Generate JWT tokens
        tokens = AuthService.generate_tokens(user_id)
        
        return jsonify({
            "status": "success",
            "message": "Authentication successful",
            "data": {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                },
                "confidence": confidence,
                **tokens
            }
        })
        
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({
            "status": "error",
            "message": "Authentication failed",
            "error": str(e)
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.
    
    Returns:
        JSON: New access token.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Verify user still exists and is active
        user = User.get_by_id(int(current_user_id))
        if not user or not user.is_active:
            return jsonify({
                "status": "error",
                "message": "User account is not active",
                "data": None
            }), 401
        
        # Generate new access token
        tokens = AuthService.generate_tokens(user.id)
        
        return jsonify({
            "status": "success",
            "message": "Token refreshed successfully",
            "data": {
                "access_token": tokens['access_token'],
                "token_type": tokens['token_type']
            }
        })
        
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to refresh token",
            "error": str(e)
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user information.
    
    Returns:
        JSON: Current user details.
    """
    try:
        user = AuthService.get_current_user()
        
        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found",
                "data": None
            }), 404
        
        return jsonify({
            "status": "success",
            "message": "User retrieved successfully",
            "data": {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at,
                    "is_active": user.is_active
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get user information",
            "error": str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (client should discard tokens).
    
    Returns:
        JSON: Logout confirmation.
    """
    try:
        # In a more complex system, we might blacklist the token here
        # For now, we just return success and let the client discard the token
        
        current_user_id = get_jwt_identity()
        logger.info(f"User {current_user_id} logged out")
        
        return jsonify({
            "status": "success",
            "message": "Logged out successfully",
            "data": None
        })
        
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return jsonify({
            "status": "error",
            "message": "Logout failed",
            "error": str(e)
        }), 500