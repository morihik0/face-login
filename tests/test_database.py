"""
Test script for database connection and initialization.
"""
import os
import sys
import logging
import sqlite3

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging before imports to avoid any logging configuration issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.database.db import init_db, test_connection, get_db_connection
from app.database.models import User, FaceEncoding, AuthLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_db_initialization():
    """Test database initialization."""
    logger.info("Testing database initialization...")
    
    # Initialize the database
    result = init_db()
    
    if result:
        logger.info("✅ Database initialization successful")
    else:
        logger.error("❌ Database initialization failed")
    
    return result

def test_db_connection():
    """Test database connection."""
    logger.info("Testing database connection...")
    
    # Test the connection
    result = test_connection()
    
    if result:
        logger.info("✅ Database connection test successful")
    else:
        logger.error("❌ Database connection test failed")
    
    return result

def test_table_creation():
    """Test that tables were created correctly."""
    logger.info("Testing table creation...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table['name'] for table in cursor.fetchall() if not table['name'].startswith('sqlite_')]
        
        expected_tables = ['users', 'face_encodings', 'auth_logs']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if not missing_tables:
            logger.info(f"✅ All expected tables exist: {', '.join(tables)}")
            
            # Check table schemas
            for table in expected_tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                logger.info(f"Table '{table}' has {len(columns)} columns")
            
            conn.close()
            return True
        else:
            logger.error(f"❌ Missing tables: {', '.join(missing_tables)}")
            conn.close()
            return False
    except sqlite3.Error as e:
        logger.error(f"Error testing table creation: {e}")
        if conn:
            conn.close()
        return False

def test_basic_operations():
    """Test basic database operations."""
    logger.info("Testing basic database operations...")
    
    try:
        # Create a test user
        test_user = User.create(name="Test User", email="test@example.com")
        
        if not test_user or not test_user.id:
            logger.error("❌ Failed to create test user")
            return False
        
        logger.info(f"✅ Created test user with ID: {test_user.id}")
        
        # Retrieve the user by ID
        retrieved_user = User.get_by_id(test_user.id)
        
        if not retrieved_user:
            logger.error("❌ Failed to retrieve user by ID")
            return False
        
        logger.info(f"✅ Retrieved user by ID: {retrieved_user.id}, Name: {retrieved_user.name}")
        
        # Update the user
        retrieved_user.name = "Updated Test User"
        update_result = retrieved_user.update()
        
        if not update_result:
            logger.error("❌ Failed to update user")
            return False
        
        # Verify the update
        updated_user = User.get_by_id(test_user.id)
        logger.info(f"✅ Updated user name: {updated_user.name}")
        
        # Create an auth log
        auth_log = AuthLog.create(user_id=test_user.id, success=True, confidence=0.95)
        
        if not auth_log or not auth_log.id:
            logger.error("❌ Failed to create auth log")
            return False
        
        logger.info(f"✅ Created auth log with ID: {auth_log.id}")
        
        # Retrieve auth logs
        logs = AuthLog.get_by_user_id(test_user.id)
        
        if not logs:
            logger.error("❌ Failed to retrieve auth logs")
            return False
        
        logger.info(f"✅ Retrieved {len(logs)} auth logs")
        
        # Clean up - delete the test user (should cascade to face_encodings and set auth_logs user_id to NULL)
        delete_result = test_user.delete()
        
        if not delete_result:
            logger.error("❌ Failed to delete test user")
            return False
        
        logger.info("✅ Deleted test user")
        
        # Verify the user is deleted
        deleted_user = User.get_by_id(test_user.id)
        
        if deleted_user:
            logger.error("❌ User still exists after deletion")
            return False
        
        logger.info("✅ User successfully deleted")
        
        return True
    except Exception as e:
        logger.error(f"Error during basic operations test: {e}")
        return False

def run_tests():
    """Run all database tests."""
    logger.info("Starting database tests...")
    
    # Run the tests
    init_result = test_db_initialization()
    conn_result = test_db_connection()
    table_result = test_table_creation()
    ops_result = test_basic_operations()
    
    # Print summary
    logger.info("\n--- Test Summary ---")
    logger.info(f"Database Initialization: {'✅ PASS' if init_result else '❌ FAIL'}")
    logger.info(f"Database Connection: {'✅ PASS' if conn_result else '❌ FAIL'}")
    logger.info(f"Table Creation: {'✅ PASS' if table_result else '❌ FAIL'}")
    logger.info(f"Basic Operations: {'✅ PASS' if ops_result else '❌ FAIL'}")
    
    all_passed = all([init_result, conn_result, table_result, ops_result])
    logger.info(f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    run_tests()