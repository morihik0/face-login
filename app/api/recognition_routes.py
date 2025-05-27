"""
Face recognition API routes.
"""
import base64
import os
import cv2
import numpy as np
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import recognition_bp
from app.database.models import User, FaceEncoding, AuthLog
from app.services.face_recognition import register_face, authenticate_face
from app.services.auth import AuthService
from app.config import STORAGE
from app.utils import create_error_response, create_success_response, validate_request_data
import logging

# Configure logger
logger = logging.getLogger(__name__)

@recognition_bp.route('/register', methods=['POST'])
@jwt_required()
def register_face_endpoint():
    """
    Register a face for a user.
    
    Expected JSON payload:
    {
        "user_id": 1,
        "image": "base64_encoded_image_data"
    }
    
    Returns:
        JSON: Registration result.
    """
    logger.info("Request to register a face")
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided",
                "data": None
            }), 400
        
        user_id = data.get('user_id')
        image_data = data.get('image')
        
        # Validate required fields
        if not user_id or not image_data:
            return jsonify({
                "status": "error",
                "message": "user_id and image are required",
                "data": None
            }), 400
        
        # Verify that the authenticated user can register faces for this user
        # (In a real system, you might want to allow admins to register for others)
        current_user_id = get_jwt_identity()
        if str(user_id) != current_user_id:
            return jsonify({
                "status": "error",
                "message": "You can only register faces for your own account",
                "data": None
            }), 403
        
        # Check if user exists
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                "status": "error",
                "message": f"User with ID {user_id} not found",
                "data": None
            }), 404
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            # Decode image
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
                
        except Exception as e:
            logger.error(f"Error decoding base64 image: {e}")
            return jsonify({
                "status": "error",
                "message": "Invalid base64 image data",
                "data": None
            }), 400
        
        # Register the face
        try:
            face_encoding_obj = register_face(user_id, image)
            
            # Get the current face count for the user
            from app.database.models import FaceEncoding as FaceEncodingModel
            face_count = FaceEncodingModel.count_by_user_id(user_id)
            
            return jsonify({
                "status": "success",
                "message": "Face registered successfully",
                "data": {
                    "user_id": user_id,
                    "face_count": face_count,
                    "image_path": face_encoding_obj.image_path
                }
            }), 201
            
        except ValueError as e:
            return jsonify({
                "status": "error",
                "message": str(e),
                "data": None
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error during face registration: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Error registering face: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to register face",
            "error": str(e)
        }), 500

@recognition_bp.route('/authenticate', methods=['POST'])
def authenticate_face_endpoint():
    """
    Authenticate a face.
    
    Expected JSON payload:
    {
        "image": "base64_encoded_image_data"
    }
    
    Returns:
        JSON: Authentication result.
    """
    logger.info("Request to authenticate a face")
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided",
                "data": None
            }), 400
        
        image_data = data.get('image')
        
        # Validate required fields
        if not image_data:
            return jsonify({
                "status": "error",
                "message": "image is required",
                "data": None
            }), 400
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            # Decode image
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
                
        except Exception as e:
            logger.error(f"Error decoding base64 image: {e}")
            return jsonify({
                "status": "error",
                "message": "Invalid base64 image data",
                "data": None
            }), 400
        
        # Authenticate the face
        try:
            success, user_id, confidence = authenticate_face(image)
            
            if success:
                # Get user details
                user = User.get_by_id(user_id)
                
                return jsonify({
                    "status": "success",
                    "message": "Authentication successful",
                    "data": {
                        "authenticated": True,
                        "user": {
                            "id": user.id,
                            "name": user.name,
                            "email": user.email
                        },
                        "confidence": confidence
                    }
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Authentication failed - no matching face found",
                    "data": {
                        "authenticated": False
                    }
                }), 401
                
        except (ValueError, Exception) as e:
            logger.error(f"Error during authentication: {e}")
            return jsonify({
                "status": "error",
                "message": str(e),
                "data": {
                    "authenticated": False
                }
            }), 400
            
    except Exception as e:
        logger.error(f"Error authenticating face: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to authenticate face",
            "error": str(e)
        }), 500

@recognition_bp.route('/history', methods=['GET'])
@jwt_required()
def get_auth_history():
    """
    Get authentication history.
    
    Query parameters:
    - user_id (optional): Filter by user ID
    - limit (optional): Number of records to return (default: 10)
    
    Returns:
        JSON: Authentication history.
    """
    logger.info("Request to get authentication history")
    
    try:
        # Get query parameters
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', default=10, type=int)
        
        # If user_id is specified, verify access
        if user_id:
            current_user_id = get_jwt_identity()
            if str(user_id) != current_user_id:
                # In a real system, you might allow admins to view any history
                return jsonify({
                    "status": "error",
                    "message": "You can only view your own authentication history",
                    "data": None
                }), 403
        
        # Validate limit
        if limit < 1 or limit > 100:
            limit = 10
        
        # Get authentication logs
        if user_id:
            # Check if user exists
            user = User.get_by_id(user_id)
            if not user:
                return jsonify({
                    "status": "error",
                    "message": f"User with ID {user_id} not found",
                    "data": None
                }), 404
            
            logs = AuthLog.get_by_user_id(user_id, limit=limit)
        else:
            logs = AuthLog.get_recent(limit=limit)
        
        # Format logs data
        history_data = []
        for log in logs:
            log_entry = {
                "id": log.id,
                "success": log.success,
                "confidence": log.confidence,
                "timestamp": log.timestamp
            }
            
            # Add user info if available
            if log.user_id:
                user = User.get_by_id(log.user_id)
                if user:
                    log_entry["user"] = {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email
                    }
            
            history_data.append(log_entry)
        
        return jsonify({
            "status": "success",
            "message": "Authentication history retrieved successfully",
            "data": {
                "history": history_data,
                "count": len(history_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving authentication history: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve authentication history",
            "error": str(e)
        }), 500