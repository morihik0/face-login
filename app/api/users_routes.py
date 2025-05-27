"""
User management API routes.
"""
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import users_bp
from app.database.models import User
from app.services.auth import AuthService
import logging

# Configure logger
logger = logging.getLogger(__name__)

@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """
    Get all users.
    
    Returns:
        JSON: List of users.
    """
    logger.info("Request to get all users")
    
    try:
        users = User.get_all()
        users_data = [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at,
                "is_active": user.is_active
            }
            for user in users
        ]
        
        return jsonify({
            "status": "success",
            "message": "Users retrieved successfully",
            "data": {
                "users": users_data,
                "count": len(users_data)
            }
        })
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve users",
            "error": str(e)
        }), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Get a specific user by ID.
    
    Args:
        user_id (int): The user ID.
        
    Returns:
        JSON: User details.
    """
    logger.info(f"Request to get user with ID: {user_id}")
    
    try:
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({
                "status": "error",
                "message": f"User with ID {user_id} not found",
                "data": None
            }), 404
        
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at,
            "is_active": user.is_active
        }
        
        return jsonify({
            "status": "success",
            "message": "User retrieved successfully",
            "data": {
                "user": user_data
            }
        })
    except Exception as e:
        logger.error(f"Error retrieving user: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve user",
            "error": str(e)
        }), 500

@users_bp.route('', methods=['POST'])
@jwt_required()
def create_user():
    """
    Create a new user.
    
    Returns:
        JSON: Created user details.
    """
    logger.info("Request to create a new user")
    
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided",
                "data": None
            }), 400
        
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({
                "status": "error",
                "message": "Name and email are required",
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
        
        # Create the user
        user = User.create(name=name, email=email)
        
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at,
            "is_active": user.is_active
        }
        
        return jsonify({
            "status": "success",
            "message": "User created successfully",
            "data": {
                "user": user_data
            }
        }), 201
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to create user",
            "error": str(e)
        }), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Update a specific user.
    
    Args:
        user_id (int): The user ID.
        
    Returns:
        JSON: Updated user details.
    """
    logger.info(f"Request to update user with ID: {user_id}")
    
    try:
        # Get the user
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({
                "status": "error",
                "message": f"User with ID {user_id} not found",
                "data": None
            }), 404
        
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided",
                "data": None
            }), 400
        
        # Update fields if provided
        if 'name' in data:
            user.name = data['name']
        
        if 'email' in data:
            # Check if new email already exists
            existing_user = User.get_by_email(data['email'])
            if existing_user and existing_user.id != user_id:
                return jsonify({
                    "status": "error",
                    "message": "User with this email already exists",
                    "data": None
                }), 409
            user.email = data['email']
        
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        # Update the user
        if user.update():
            user_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at,
                "is_active": user.is_active
            }
            
            return jsonify({
                "status": "success",
                "message": "User updated successfully",
                "data": {
                    "user": user_data
                }
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to update user",
                "data": None
            }), 500
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to update user",
            "error": str(e)
        }), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Delete a specific user.
    
    Args:
        user_id (int): The user ID.
        
    Returns:
        JSON: Deletion confirmation.
    """
    logger.info(f"Request to delete user with ID: {user_id}")
    
    try:
        # Get the user
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({
                "status": "error",
                "message": f"User with ID {user_id} not found",
                "data": None
            }), 404
        
        # Delete the user
        if user.delete():
            return jsonify({
                "status": "success",
                "message": f"User with ID {user_id} deleted successfully",
                "data": None
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to delete user",
                "data": None
            }), 500
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to delete user",
            "error": str(e)
        }), 500