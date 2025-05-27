"""
Utility functions for the Face Login application.
"""
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def create_error_response(message, status_code=400, error_details=None):
    """
    Create a standardized error response.
    
    Args:
        message (str): Error message.
        status_code (int): HTTP status code.
        error_details (str, optional): Additional error details.
        
    Returns:
        tuple: JSON response and status code.
    """
    response_data = {
        "status": "error",
        "message": message,
        "data": None
    }
    
    if error_details:
        response_data["error"] = error_details
    
    return jsonify(response_data), status_code


def create_success_response(message, data=None, status_code=200):
    """
    Create a standardized success response.
    
    Args:
        message (str): Success message.
        data (dict, optional): Response data.
        status_code (int): HTTP status code.
        
    Returns:
        tuple: JSON response and status code.
    """
    response_data = {
        "status": "success",
        "message": message,
        "data": data
    }
    
    return jsonify(response_data), status_code


def validate_request_data(data, required_fields):
    """
    Validate request data for required fields.
    
    Args:
        data (dict): Request data.
        required_fields (list): List of required field names.
        
    Returns:
        tuple: (is_valid, missing_fields)
    """
    if not data:
        return False, ["No data provided"]
    
    missing_fields = []
    for field in required_fields:
        if not data.get(field):
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields