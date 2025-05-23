"""
Main entry point for the Face Login application.
"""
import os
import logging
from app import create_app
from app.config import STORAGE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup():
    """
    Set up the application by creating necessary directories.
    """
    # Create directory for face images if it doesn't exist
    face_images_dir = STORAGE['face_images_dir']
    
    if not os.path.exists(face_images_dir):
        try:
            os.makedirs(face_images_dir)
            logger.info(f"Created face images directory: {face_images_dir}")
        except Exception as e:
            logger.error(f"Failed to create face images directory: {e}")
            return False
    
    logger.info("Application setup completed successfully")
    return True

def main():
    """
    Main function to run the application.
    """
    # Set up the application
    setup_result = setup()
    
    if not setup_result:
        logger.error("Application setup failed")
        return
    
    # Create the Flask application
    app = create_app()
    
    # Run the application
    port = int(os.environ.get('PORT', 5001))  # Changed default port to 5001 to avoid conflicts with AirPlay
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Starting Flask application on port {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == "__main__":
    main()