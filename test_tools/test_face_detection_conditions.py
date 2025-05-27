"""
Test script for face detection under various conditions.

This script tests the face detection functionality with various test images
under different conditions (brightness, size, quality, angles, expressions,
occlusions, backgrounds) and generates a report on the detection success rate.
"""
import cv2
import numpy as np
import os
import sys
import time
import pandas as pd
from tabulate import tabulate
from app.services.face_detection import (
    detect_faces,
    detect_single_face,
    validate_face_image,
    FaceDetectionError,
    MultipleFacesError
)

# Define test image directories
TEST_IMAGES_DIR = 'tests/test_images'
CONDITION_DIRS = [
    'brightness',
    'sizes',
    'quality',
    'angles',
    'expressions',
    'occlusions',
    'backgrounds'
]

def test_face_detection(image_path):
    """Test face detection on a single image."""
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        return {
            'success': False,
            'error': 'Failed to load image',
            'face_count': 0,
            'time_ms': 0
        }
    
    # Measure time
    start_time = time.time()
    
    try:
        # Try to detect faces
        face_locations = detect_faces(image)
        success = True
        error = None
        face_count = len(face_locations)
    except FaceDetectionError as e:
        success = False
        error = str(e)
        face_count = 0
    except Exception as e:
        success = False
        error = f"Unexpected error: {str(e)}"
        face_count = 0
    
    # Calculate elapsed time
    elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    return {
        'success': success,
        'error': error,
        'face_count': face_count,
        'time_ms': elapsed_time
    }

def test_face_validation(image_path):
    """Test face image validation on a single image."""
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        return {
            'valid': False,
            'message': 'Failed to load image'
        }
    
    # Validate the image
    is_valid, message = validate_face_image(image)
    
    return {
        'valid': is_valid,
        'message': message
    }

def run_tests():
    """Run face detection tests on all test images."""
    results = []
    
    # Test base images
    base_images = [
        'single_face_test.jpg',
        'multi_face_test.jpg',
        'test_face.jpg',
        'no_face.jpg'
    ]
    
    for image_name in base_images:
        image_path = os.path.join(TEST_IMAGES_DIR, image_name)
        if os.path.exists(image_path):
            print(f"Testing base image: {image_name}")
            detection_result = test_face_detection(image_path)
            validation_result = test_face_validation(image_path)
            
            results.append({
                'category': 'base',
                'image': image_name,
                'detection_success': detection_result['success'],
                'face_count': detection_result['face_count'],
                'detection_error': detection_result['error'],
                'detection_time_ms': detection_result['time_ms'],
                'validation_valid': validation_result['valid'],
                'validation_message': validation_result['message']
            })
    
    # Test images in condition directories
    for condition_dir in CONDITION_DIRS:
        dir_path = os.path.join(TEST_IMAGES_DIR, condition_dir)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"Testing condition: {condition_dir}")
            
            for image_name in os.listdir(dir_path):
                if image_name.endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(dir_path, image_name)
                    print(f"  Testing image: {image_name}")
                    
                    detection_result = test_face_detection(image_path)
                    validation_result = test_face_validation(image_path)
                    
                    results.append({
                        'category': condition_dir,
                        'image': image_name,
                        'detection_success': detection_result['success'],
                        'face_count': detection_result['face_count'],
                        'detection_error': detection_result['error'],
                        'detection_time_ms': detection_result['time_ms'],
                        'validation_valid': validation_result['valid'],
                        'validation_message': validation_result['message']
                    })
    
    return results

def generate_report(results):
    """Generate a report from the test results."""
    # Convert results to DataFrame
    df = pd.DataFrame(results)
    
    # Calculate overall statistics
    total_images = len(df)
    successful_detections = df['detection_success'].sum()
    detection_success_rate = successful_detections / total_images * 100
    valid_images = df['validation_valid'].sum()
    validation_success_rate = valid_images / total_images * 100
    avg_detection_time = df['detection_time_ms'].mean()
    
    print("\n===== FACE DETECTION TEST REPORT =====\n")
    print(f"Total images tested: {total_images}")
    print(f"Successful detections: {successful_detections} ({detection_success_rate:.2f}%)")
    print(f"Valid images: {valid_images} ({validation_success_rate:.2f}%)")
    print(f"Average detection time: {avg_detection_time:.2f} ms")
    
    # Statistics by category
    print("\n----- Results by Category -----\n")
    category_stats = df.groupby('category').agg({
        'detection_success': ['count', 'sum', lambda x: x.sum() / len(x) * 100],
        'validation_valid': ['sum', lambda x: x.sum() / len(x) * 100],
        'detection_time_ms': 'mean'
    })
    
    # Rename columns for better readability
    category_stats.columns = [
        'Total', 'Detected', 'Detection Rate (%)', 
        'Valid', 'Validation Rate (%)', 
        'Avg Time (ms)'
    ]
    
    print(tabulate(category_stats, headers='keys', tablefmt='grid'))
    
    # Detailed results for failed detections
    failed_detections = df[~df['detection_success']]
    if len(failed_detections) > 0:
        print("\n----- Failed Detections -----\n")
        failed_summary = failed_detections[['category', 'image', 'detection_error']]
        print(tabulate(failed_summary, headers='keys', tablefmt='grid'))
    
    # Save results to CSV
    output_dir = 'tests/results'
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, 'face_detection_test_results.csv')
    df.to_csv(csv_path, index=False)
    print(f"\nDetailed results saved to: {csv_path}")
    
    # Generate summary by image type
    summary_path = os.path.join(output_dir, 'face_detection_test_summary.csv')
    category_stats.to_csv(summary_path)
    print(f"Summary by category saved to: {summary_path}")

def main():
    """Main function."""
    print("Starting face detection tests under various conditions...")
    
    # Run the tests
    results = run_tests()
    
    # Generate the report
    generate_report(results)
    
    print("\nFace detection tests completed!")

if __name__ == "__main__":
    main()