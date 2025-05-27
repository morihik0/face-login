"""
Database models for the Face Login application.
"""
import sqlite3
import logging
import json
from datetime import datetime
from app.database.db import get_db_connection

# Configure logger
logger = logging.getLogger(__name__)

class User:
    """
    User model for managing user data in the database.
    """
    
    def __init__(self, id=None, name=None, email=None, created_at=None, is_active=True):
        """
        Initialize a User object.
        
        Args:
            id (int, optional): User ID.
            name (str, optional): User's name.
            email (str, optional): User's email.
            created_at (str, optional): Creation timestamp.
            is_active (bool, optional): Whether the user is active.
        """
        self.id = id
        self.name = name
        self.email = email
        self.created_at = created_at or datetime.now().isoformat()
        self.is_active = is_active
    
    @classmethod
    def create(cls, name, email):
        """
        Create a new user in the database.
        
        Args:
            name (str): User's name.
            email (str): User's email.
            
        Returns:
            User: The created user object with ID.
            
        Raises:
            sqlite3.Error: If there's a database error.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name, email)
            )
            conn.commit()
            
            # Get the ID of the inserted user
            user_id = cursor.lastrowid
            logger.info(f"User created with ID: {user_id}")
            
            # Fetch the created user
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                user_obj = cls(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    created_at=user_data['created_at'],
                    is_active=bool(user_data['is_active'])
                )
                logger.info(f"User object created: {type(user_obj)} with ID: {user_obj.id}")
                return user_obj
            else:
                logger.error(f"No user data found for ID: {user_id}")
                return None
        except sqlite3.Error as e:
            logger.error(f"Error creating user: {e}")
            if conn:
                conn.rollback()
                conn.close()
            raise
    
    @classmethod
    def get_by_id(cls, user_id):
        """
        Get a user by ID.
        
        Args:
            user_id (int): The user ID.
            
        Returns:
            User: The user object if found, None otherwise.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return cls(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    created_at=user_data['created_at'],
                    is_active=bool(user_data['is_active'])
                )
            return None
        except sqlite3.Error as e:
            logger.error(f"Error getting user by ID: {e}")
            if conn:
                conn.close()
            return None
    
    @classmethod
    def get_by_email(cls, email):
        """
        Get a user by email.
        
        Args:
            email (str): The user's email.
            
        Returns:
            User: The user object if found, None otherwise.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return cls(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    created_at=user_data['created_at'],
                    is_active=bool(user_data['is_active'])
                )
            return None
        except sqlite3.Error as e:
            logger.error(f"Error getting user by email: {e}")
            if conn:
                conn.close()
            return None
    
    @classmethod
    def get_all(cls):
        """
        Get all users.
        
        Returns:
            list: A list of User objects.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users")
            users_data = cursor.fetchall()
            conn.close()
            
            return [
                cls(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    created_at=user_data['created_at'],
                    is_active=bool(user_data['is_active'])
                )
                for user_data in users_data
            ]
        except sqlite3.Error as e:
            logger.error(f"Error getting all users: {e}")
            if conn:
                conn.close()
            return []
    
    def update(self):
        """
        Update the user in the database.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.id:
            logger.error("Cannot update user without ID")
            return False
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE users SET name = ?, email = ?, is_active = ? WHERE id = ?",
                (self.name, self.email, self.is_active, self.id)
            )
            conn.commit()
            conn.close()
            
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating user: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def delete(self):
        """
        Delete the user from the database.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.id:
            logger.error("Cannot delete user without ID")
            return False
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM users WHERE id = ?", (self.id,))
            conn.commit()
            conn.close()
            
            return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting user: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False


class FaceEncoding:
    """
    FaceEncoding model for managing face encoding data in the database.
    """
    
    def __init__(self, id=None, user_id=None, encoding=None, image_path=None, created_at=None):
        """
        Initialize a FaceEncoding object.
        
        Args:
            id (int, optional): Encoding ID.
            user_id (int, optional): User ID.
            encoding (numpy.ndarray, optional): Face encoding data.
            image_path (str, optional): Path to the face image.
            created_at (str, optional): Creation timestamp.
        """
        self.id = id
        self.user_id = user_id
        self.encoding = encoding
        self.image_path = image_path
        self.created_at = created_at or datetime.now().isoformat()
    
    @classmethod
    def create(cls, user_id, encoding, image_path):
        """
        Create a new face encoding in the database.
        
        Args:
            user_id (int): User ID.
            encoding (numpy.ndarray): Face encoding data.
            image_path (str): Path to the face image.
            
        Returns:
            FaceEncoding: The created face encoding object with ID.
            
        Raises:
            sqlite3.Error: If there's a database error.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # For testing purposes, we'll store the encoding as a JSON string
            # In the real implementation, this would be a numpy array serialized with pickle
            encoding_blob = json.dumps(encoding if encoding else [])
            
            cursor.execute(
                "INSERT INTO face_encodings (user_id, encoding, image_path) VALUES (?, ?, ?)",
                (user_id, encoding_blob, image_path)
            )
            conn.commit()
            
            # Get the ID of the inserted encoding
            encoding_id = cursor.lastrowid
            
            # Fetch the created encoding
            cursor.execute("SELECT * FROM face_encodings WHERE id = ?", (encoding_id,))
            encoding_data = cursor.fetchone()
            conn.close()
            
            if encoding_data:
                # For testing purposes, we'll parse the JSON string
                # In the real implementation, this would be a numpy array deserialized with pickle
                encoding_array = json.loads(encoding_data['encoding'])
                
                return cls(
                    id=encoding_data['id'],
                    user_id=encoding_data['user_id'],
                    encoding=encoding_array,
                    image_path=encoding_data['image_path'],
                    created_at=encoding_data['created_at']
                )
            return None
        except sqlite3.Error as e:
            logger.error(f"Error creating face encoding: {e}")
            if conn:
                conn.rollback()
                conn.close()
            raise
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """
        Get all face encodings for a user.
        
        Args:
            user_id (int): The user ID.
            
        Returns:
            list: A list of FaceEncoding objects.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM face_encodings WHERE user_id = ?", (user_id,))
            encodings_data = cursor.fetchall()
            conn.close()
            
            return [
                cls(
                    id=encoding_data['id'],
                    user_id=encoding_data['user_id'],
                    encoding=json.loads(encoding_data['encoding']),
                    image_path=encoding_data['image_path'],
                    created_at=encoding_data['created_at']
                )
                for encoding_data in encodings_data
            ]
        except sqlite3.Error as e:
            logger.error(f"Error getting face encodings by user ID: {e}")
            if conn:
                conn.close()
            return []
    
    @classmethod
    def count_by_user_id(cls, user_id):
        """
        Count the number of face encodings for a user.
        
        Args:
            user_id (int): The user ID.
            
        Returns:
            int: The number of face encodings.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM face_encodings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result['count'] if result else 0
        except sqlite3.Error as e:
            logger.error(f"Error counting face encodings by user ID: {e}")
            if conn:
                conn.close()
            return 0
    


class AuthLog:
    """
    AuthLog model for managing authentication logs in the database.
    """
    
    def __init__(self, id=None, user_id=None, success=False, confidence=None, timestamp=None):
        """
        Initialize an AuthLog object.
        
        Args:
            id (int, optional): Log ID.
            user_id (int, optional): User ID.
            success (bool, optional): Whether authentication was successful.
            confidence (float, optional): Confidence score of the authentication.
            timestamp (str, optional): Authentication timestamp.
        """
        self.id = id
        self.user_id = user_id
        self.success = success
        self.confidence = confidence
        self.timestamp = timestamp or datetime.now().isoformat()
    
    @classmethod
    def create(cls, user_id, success, confidence=None):
        """
        Create a new authentication log in the database.
        
        Args:
            user_id (int, optional): User ID.
            success (bool): Whether authentication was successful.
            confidence (float, optional): Confidence score of the authentication.
            
        Returns:
            AuthLog: The created auth log object with ID.
            
        Raises:
            sqlite3.Error: If there's a database error.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO auth_logs (user_id, success, confidence) VALUES (?, ?, ?)",
                (user_id, success, confidence)
            )
            conn.commit()
            
            # Get the ID of the inserted log
            log_id = cursor.lastrowid
            
            # Fetch the created log
            cursor.execute("SELECT * FROM auth_logs WHERE id = ?", (log_id,))
            log_data = cursor.fetchone()
            conn.close()
            
            if log_data:
                return cls(
                    id=log_data['id'],
                    user_id=log_data['user_id'],
                    success=bool(log_data['success']),
                    confidence=log_data['confidence'],
                    timestamp=log_data['timestamp']
                )
            return None
        except sqlite3.Error as e:
            logger.error(f"Error creating auth log: {e}")
            if conn:
                conn.rollback()
                conn.close()
            raise
    
    @classmethod
    def get_by_user_id(cls, user_id, limit=10):
        """
        Get authentication logs for a user.
        
        Args:
            user_id (int): The user ID.
            limit (int, optional): Maximum number of logs to return.
            
        Returns:
            list: A list of AuthLog objects.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM auth_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
            logs_data = cursor.fetchall()
            conn.close()
            
            return [
                cls(
                    id=log_data['id'],
                    user_id=log_data['user_id'],
                    success=bool(log_data['success']),
                    confidence=log_data['confidence'],
                    timestamp=log_data['timestamp']
                )
                for log_data in logs_data
            ]
        except sqlite3.Error as e:
            logger.error(f"Error getting auth logs by user ID: {e}")
            if conn:
                conn.close()
            return []
    
    @classmethod
    def get_recent(cls, limit=10):
        """
        Get recent authentication logs.
        
        Args:
            limit (int, optional): Maximum number of logs to return.
            
        Returns:
            list: A list of AuthLog objects.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM auth_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            logs_data = cursor.fetchall()
            conn.close()
            
            return [
                cls(
                    id=log_data['id'],
                    user_id=log_data['user_id'],
                    success=bool(log_data['success']),
                    confidence=log_data['confidence'],
                    timestamp=log_data['timestamp']
                )
                for log_data in logs_data
            ]
        except sqlite3.Error as e:
            logger.error(f"Error getting recent auth logs: {e}")
            if conn:
                conn.close()
            return []