"""
Database connection and initialization module.
"""
import os
import sqlite3
import logging
from pathlib import Path
from app.config import DATABASE

# Configure logger
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Create a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: A connection object to the database.
    """
    try:
        # Ensure the directory exists
        db_path = DATABASE['path']
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connect to the database with row factory for dictionary-like rows
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        logger.debug(f"Connected to database at {db_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def create_tables(conn):
    """
    Create the necessary tables in the database if they don't exist.
    
    Args:
        conn (sqlite3.Connection): A connection to the database.
    """
    try:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        ''')
        
        # Create face_encodings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_encodings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            encoding BLOB NOT NULL,
            image_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        ''')
        
        # Create auth_logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            success BOOLEAN NOT NULL,
            confidence REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
        ''')
        
        conn.commit()
        logger.info("Database tables created successfully")
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Error creating tables: {e}")
        raise

def init_db():
    """
    Initialize the database by creating the necessary tables.
    
    Returns:
        bool: True if initialization was successful, False otherwise.
    """
    try:
        # Create the database directory if it doesn't exist
        db_dir = os.path.dirname(DATABASE['path'])
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")
        
        # Connect to the database and create tables
        conn = get_db_connection()
        create_tables(conn)
        conn.close()
        
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def test_connection():
    """
    Test the database connection by executing a simple query.
    
    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        conn.close()
        
        logger.info(f"Database connection test successful. SQLite version: {version}")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize the database
    init_db()
    
    # Test the connection
    test_connection()