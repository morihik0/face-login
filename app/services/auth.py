"""
Authentication service for JWT token management.
"""
import logging
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.models import User

# Configure logger
logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling authentication and JWT tokens."""
    
    @staticmethod
    def generate_tokens(user_id):
        """
        Generate access and refresh tokens for a user.
        
        Args:
            user_id (int): The user ID.
            
        Returns:
            dict: Dictionary containing access_token and refresh_token.
        """
        # Create tokens with user_id as identity
        access_token = create_access_token(
            identity=str(user_id),
            expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(
            identity=str(user_id),
            expires_delta=timedelta(days=30)
        )
        
        logger.info(f"Generated tokens for user {user_id}")
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        }
    
    @staticmethod
    def authenticate_user(email, password=None):
        """
        Authenticate a user by email and password.
        
        Args:
            email (str): User's email.
            password (str, optional): User's password (for future use).
            
        Returns:
            User: The authenticated user object or None.
        """
        try:
            user = User.get_by_email(email)
            
            if not user:
                logger.warning(f"Authentication failed: User not found with email {email}")
                return None
            
            if not user.is_active:
                logger.warning(f"Authentication failed: User {user.id} is inactive")
                return None
            
            # For now, we're using face authentication only
            # In the future, password authentication can be added here
            # if password and not check_password_hash(user.password_hash, password):
            #     return None
            
            logger.info(f"User {user.id} authenticated successfully")
            return user
            
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return None
    
    @staticmethod
    def get_current_user():
        """
        Get the current authenticated user from JWT token.
        
        Returns:
            User: The current user object or None.
        """
        try:
            user_id = get_jwt_identity()
            if not user_id:
                return None
            
            user = User.get_by_id(int(user_id))
            if not user or not user.is_active:
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None
    
    @staticmethod
    def validate_token_user(user_id):
        """
        Validate that the token user matches the requested resource.
        
        Args:
            user_id (int): The user ID to validate against.
            
        Returns:
            bool: True if the current user matches or is admin, False otherwise.
        """
        try:
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return False
            
            # Check if the current user is the same as requested
            # In the future, admin role check can be added here
            return str(user_id) == current_user_id
            
        except Exception as e:
            logger.error(f"Error validating token user: {e}")
            return False

# Rate limiting configurations
RATE_LIMIT_RULES = {
    'authentication': '5 per minute',
    'registration': '10 per hour',
    'api_default': '100 per minute'
}

def get_rate_limit(endpoint_type='api_default'):
    """
    Get rate limit for specific endpoint type.
    
    Args:
        endpoint_type (str): Type of endpoint.
        
    Returns:
        str: Rate limit string.
    """
    return RATE_LIMIT_RULES.get(endpoint_type, RATE_LIMIT_RULES['api_default'])