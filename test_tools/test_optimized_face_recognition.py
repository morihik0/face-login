"""
Test script for optimized face recognition functions.

This script tests the optimized face detection and recognition functions
and compares their performance and accuracy with the original functions.
"""
import cv2
import numpy as np
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
from tqdm import tqdm

from app.services.face_detection import (
    detect_faces,
    detect_single_face,
    validate_face_image,
    extract_face_encoding,
    FaceDetectionError,
    MultipleFacesError
)
from app.services.face_recognition import (
    register_face,
    authenticate_face,
    get_recognition_threshold,
    set_recognition_threshold,
    compare_faces
)

from optimize_face_recognition import (
    preprocess_image,
    optimized_detect_faces,
    optimized_extract_face_encoding
)

# Define paths
TEST_IMAGES_DIR = 'tests/test_images'
OUTPUT_DIR = 'tests/results/optimization_test'

def load_test_image(image_path):
    """Load a test image from the given path."""
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return None
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image from {image_path}")
        return None
    
    return image

def test_preprocessing(image_path):
    """Test image preprocessing function."""
    print(f"\nTesting image preprocessing on {os.path.basename(image_path)}...")
    
    # Load the image
    original_image = load_test_image(image_path)
    if original_image is None:
        return
    
    # Get original image properties
    original_height, original_width = original_image.shape[:2]
    original_hsv = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
    original_brightness = np.mean(original_hsv[:, :, 2])
    
    print(f"Original image dimensions: {original_width}x{original_height}")
    print(f"Original image brightness: {original_brightness:.2f}")
    
    # Preprocess the image
    start_time = time.time()
    processed_image = preprocess_image(original_image)
    processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Get processed image properties
    processed_height, processed_width = processed_image.shape[:2]
    processed_hsv = cv2.cvtColor(processed_image, cv2.COLOR_BGR2HSV)
    processed_brightness = np.mean(processed_hsv[:, :, 2])
    
    print(f"Processed image dimensions: {processed_width}x{processed_height}")
    print(f"Processed image brightness: {processed_brightness:.2f}")
    print(f"Processing time: {processing_time:.2f} ms")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Save original and processed images
    original_output_path = os.path.join(OUTPUT_DIR, f"original_{os.path.basename(image_path)}")
    processed_output_path = os.path.join(OUTPUT_DIR, f"processed_{os.path.basename(image_path)}")
    
    cv2.imwrite(original_output_path, original_image)
    cv2.imwrite(processed_output_path, processed_image)
    
    print(f"Original image saved to {original_output_path}")
    print(f"Processed image saved to {processed_output_path}")
    
    # Create side-by-side comparison
    # Resize images to the same height if needed
    if original_height != processed_height:
        scale_factor = processed_height / original_height
        original_resized = cv2.resize(original_image, (int(original_width * scale_factor), processed_height))
    else:
        original_resized = original_image
    
    # Create side-by-side image
    comparison = np.hstack((original_resized, processed_image))
    comparison_path = os.path.join(OUTPUT_DIR, f"comparison_{os.path.basename(image_path)}")
    cv2.imwrite(comparison_path, comparison)
    
    print(f"Side-by-side comparison saved to {comparison_path}")
    
    return {
        'original_width': original_width,
        'original_height': original_height,
        'original_brightness': original_brightness,
        'processed_width': processed_width,
        'processed_height': processed_height,
        'processed_brightness': processed_brightness,
        'processing_time': processing_time
    }

def test_face_detection(image_path):
    """Test face detection functions."""
    print(f"\nTesting face detection on {os.path.basename(image_path)}...")
    
    # Load the image
    image = load_test_image(image_path)
    if image is None:
        return
    
    # Test original detect_faces
    print("Testing original detect_faces...")
    start_time = time.time()
    try:
        original_face_locations = detect_faces(image)
        original_success = True
        original_face_count = len(original_face_locations)
        original_error = None
    except Exception as e:
        original_success = False
        original_face_count = 0
        original_error = str(e)
    original_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Test optimized detect_faces
    print("Testing optimized detect_faces...")
    start_time = time.time()
    try:
        optimized_face_locations = optimized_detect_faces(image)
        optimized_success = True
        optimized_face_count = len(optimized_face_locations)
        optimized_error = None
    except Exception as e:
        optimized_success = False
        optimized_face_count = 0
        optimized_error = str(e)
    optimized_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Print results
    print(f"Original detect_faces: {'Success' if original_success else 'Failed'}")
    if original_success:
        print(f"  Detected {original_face_count} faces")
    else:
        print(f"  Error: {original_error}")
    print(f"  Time: {original_time:.2f} ms")
    
    print(f"Optimized detect_faces: {'Success' if optimized_success else 'Failed'}")
    if optimized_success:
        print(f"  Detected {optimized_face_count} faces")
    else:
        print(f"  Error: {optimized_error}")
    print(f"  Time: {optimized_time:.2f} ms")
    
    # Create visualizations if successful
    if original_success or optimized_success:
        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Draw face rectangles on original image
        if original_success:
            original_result = image.copy()
            for face_location in original_face_locations:
                top, right, bottom, left = face_location
                cv2.rectangle(original_result, (left, top), (right, bottom), (0, 255, 0), 2)
            
            original_result_path = os.path.join(OUTPUT_DIR, f"original_detect_{os.path.basename(image_path)}")
            cv2.imwrite(original_result_path, original_result)
            print(f"Original detection result saved to {original_result_path}")
        
        # Draw face rectangles on optimized image
        if optimized_success:
            optimized_result = image.copy()
            for face_location in optimized_face_locations:
                top, right, bottom, left = face_location
                cv2.rectangle(optimized_result, (left, top), (right, bottom), (0, 0, 255), 2)
            
            optimized_result_path = os.path.join(OUTPUT_DIR, f"optimized_detect_{os.path.basename(image_path)}")
            cv2.imwrite(optimized_result_path, optimized_result)
            print(f"Optimized detection result saved to {optimized_result_path}")
        
        # Create side-by-side comparison if both successful
        if original_success and optimized_success:
            comparison = np.hstack((original_result, optimized_result))
            comparison_path = os.path.join(OUTPUT_DIR, f"comparison_detect_{os.path.basename(image_path)}")
            cv2.imwrite(comparison_path, comparison)
            print(f"Side-by-side detection comparison saved to {comparison_path}")
    
    return {
        'original_success': original_success,
        'original_face_count': original_face_count,
        'original_time': original_time,
        'original_error': original_error,
        'optimized_success': optimized_success,
        'optimized_face_count': optimized_face_count,
        'optimized_time': optimized_time,
        'optimized_error': optimized_error,
        'speedup': original_time / optimized_time if optimized_time > 0 else 0
    }

def test_face_encoding(image_path):
    """Test face encoding functions."""
    print(f"\nTesting face encoding on {os.path.basename(image_path)}...")
    
    # Load the image
    image = load_test_image(image_path)
    if image is None:
        return
    
    # Test original extract_face_encoding
    print("Testing original extract_face_encoding...")
    start_time = time.time()
    try:
        original_encoding = extract_face_encoding(image)
        original_success = True
        original_encoding_size = len(original_encoding)
        original_error = None
    except Exception as e:
        original_success = False
        original_encoding_size = 0
        original_error = str(e)
    original_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Test optimized extract_face_encoding
    print("Testing optimized extract_face_encoding...")
    start_time = time.time()
    try:
        optimized_encoding = optimized_extract_face_encoding(image)
        optimized_success = True
        optimized_encoding_size = len(optimized_encoding)
        optimized_error = None
    except Exception as e:
        optimized_success = False
        optimized_encoding_size = 0
        optimized_error = str(e)
    optimized_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Print results
    print(f"Original extract_face_encoding: {'Success' if original_success else 'Failed'}")
    if original_success:
        print(f"  Encoding size: {original_encoding_size}")
    else:
        print(f"  Error: {original_error}")
    print(f"  Time: {original_time:.2f} ms")
    
    print(f"Optimized extract_face_encoding: {'Success' if optimized_success else 'Failed'}")
    if optimized_success:
        print(f"  Encoding size: {optimized_encoding_size}")
    else:
        print(f"  Error: {optimized_error}")
    print(f"  Time: {optimized_time:.2f} ms")
    
    # Compare encodings if both successful
    if original_success and optimized_success:
        # Calculate similarity between encodings
        similarity = 1 - np.linalg.norm(original_encoding - optimized_encoding)
        print(f"Encoding similarity: {similarity:.4f}")
    
    return {
        'original_success': original_success,
        'original_encoding_size': original_encoding_size,
        'original_time': original_time,
        'original_error': original_error,
        'optimized_success': optimized_success,
        'optimized_encoding_size': optimized_encoding_size,
        'optimized_time': optimized_time,
        'optimized_error': optimized_error,
        'speedup': original_time / optimized_time if optimized_time > 0 else 0,
        'similarity': similarity if original_success and optimized_success else None
    }

def run_tests():
    """Run all tests."""
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Test images
    test_images = [
        os.path.join(TEST_IMAGES_DIR, 'single_face_test.jpg'),
        os.path.join(TEST_IMAGES_DIR, 'multi_face_test.jpg'),
        os.path.join(TEST_IMAGES_DIR, 'brightness', 'single_face_test_bright.jpg'),
        os.path.join(TEST_IMAGES_DIR, 'brightness', 'single_face_test_dark.jpg'),
        os.path.join(TEST_IMAGES_DIR, 'sizes', 'single_face_test_large.jpg'),
        os.path.join(TEST_IMAGES_DIR, 'sizes', 'single_face_test_small.jpg'),
        os.path.join(TEST_IMAGES_DIR, 'occlusions', 'single_face_test_sunglasses.jpg'),
        os.path.join(TEST_IMAGES_DIR, 'backgrounds', 'single_face_test_white_bg.jpg')
    ]
    
    preprocessing_results = []
    detection_results = []
    encoding_results = []
    
    for image_path in test_images:
        if os.path.exists(image_path):
            # Test preprocessing
            preprocessing_result = test_preprocessing(image_path)
            if preprocessing_result:
                preprocessing_result['image'] = os.path.basename(image_path)
                preprocessing_results.append(preprocessing_result)
            
            # Test face detection
            detection_result = test_face_detection(image_path)
            if detection_result:
                detection_result['image'] = os.path.basename(image_path)
                detection_results.append(detection_result)
            
            # Test face encoding
            encoding_result = test_face_encoding(image_path)
            if encoding_result:
                encoding_result['image'] = os.path.basename(image_path)
                encoding_results.append(encoding_result)
        else:
            print(f"Warning: Image not found at {image_path}")
    
    # Generate summary report
    generate_report(preprocessing_results, detection_results, encoding_results)

def generate_report(preprocessing_results, detection_results, encoding_results):
    """Generate a summary report of the test results."""
    print("\n===== OPTIMIZED FACE RECOGNITION TEST REPORT =====\n")
    
    # Preprocessing summary
    if preprocessing_results:
        print("----- Image Preprocessing Summary -----\n")
        
        # Convert to DataFrame
        df_preprocessing = pd.DataFrame(preprocessing_results)
        
        # Calculate averages
        avg_size_reduction = 1 - (df_preprocessing['processed_width'] * df_preprocessing['processed_height']).mean() / (df_preprocessing['original_width'] * df_preprocessing['original_height']).mean()
        avg_brightness_change = (df_preprocessing['processed_brightness'] - df_preprocessing['original_brightness']).abs().mean()
        avg_processing_time = df_preprocessing['processing_time'].mean()
        
        print(f"Average size reduction: {avg_size_reduction:.2%}")
        print(f"Average brightness adjustment: {avg_brightness_change:.2f}")
        print(f"Average processing time: {avg_processing_time:.2f} ms")
        
        # Save detailed results to CSV
        preprocessing_csv = os.path.join(OUTPUT_DIR, 'preprocessing_results.csv')
        df_preprocessing.to_csv(preprocessing_csv, index=False)
        print(f"Detailed preprocessing results saved to {preprocessing_csv}")
    
    # Face detection summary
    if detection_results:
        print("\n----- Face Detection Summary -----\n")
        
        # Convert to DataFrame
        df_detection = pd.DataFrame(detection_results)
        
        # Calculate success rates
        original_success_rate = df_detection['original_success'].mean() * 100
        optimized_success_rate = df_detection['optimized_success'].mean() * 100
        
        # Calculate average times
        original_avg_time = df_detection['original_time'].mean()
        optimized_avg_time = df_detection['optimized_time'].mean()
        avg_speedup = df_detection['speedup'].mean()
        
        print(f"Original success rate: {original_success_rate:.2f}%")
        print(f"Optimized success rate: {optimized_success_rate:.2f}%")
        print(f"Original average time: {original_avg_time:.2f} ms")
        print(f"Optimized average time: {optimized_avg_time:.2f} ms")
        print(f"Average speedup: {avg_speedup:.2f}x")
        
        # Save detailed results to CSV
        detection_csv = os.path.join(OUTPUT_DIR, 'detection_results.csv')
        df_detection.to_csv(detection_csv, index=False)
        print(f"Detailed detection results saved to {detection_csv}")
        
        # Create bar chart of detection times
        plt.figure(figsize=(12, 6))
        
        # Filter for successful detections
        successful_df = df_detection[df_detection['original_success'] & df_detection['optimized_success']]
        
        if not successful_df.empty:
            images = successful_df['image']
            original_times = successful_df['original_time']
            optimized_times = successful_df['optimized_time']
            
            x = np.arange(len(images))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(12, 6))
            rects1 = ax.bar(x - width/2, original_times, width, label='Original')
            rects2 = ax.bar(x + width/2, optimized_times, width, label='Optimized')
            
            ax.set_title('Face Detection Time Comparison')
            ax.set_xlabel('Image')
            ax.set_ylabel('Time (ms)')
            ax.set_xticks(x)
            ax.set_xticklabels(images, rotation=45)
            ax.legend()
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            detection_chart = os.path.join(OUTPUT_DIR, 'detection_time_comparison.png')
            plt.savefig(detection_chart)
            print(f"Detection time comparison chart saved to {detection_chart}")
    
    # Face encoding summary
    if encoding_results:
        print("\n----- Face Encoding Summary -----\n")
        
        # Convert to DataFrame
        df_encoding = pd.DataFrame(encoding_results)
        
        # Calculate success rates
        original_success_rate = df_encoding['original_success'].mean() * 100
        optimized_success_rate = df_encoding['optimized_success'].mean() * 100
        
        # Calculate average times
        original_avg_time = df_encoding['original_time'].mean()
        optimized_avg_time = df_encoding['optimized_time'].mean()
        avg_speedup = df_encoding['speedup'].mean()
        
        # Calculate average similarity
        similarity_values = df_encoding['similarity'].dropna()
        avg_similarity = similarity_values.mean() if not similarity_values.empty else None
        
        print(f"Original success rate: {original_success_rate:.2f}%")
        print(f"Optimized success rate: {optimized_success_rate:.2f}%")
        print(f"Original average time: {original_avg_time:.2f} ms")
        print(f"Optimized average time: {optimized_avg_time:.2f} ms")
        print(f"Average speedup: {avg_speedup:.2f}x")
        if avg_similarity is not None:
            print(f"Average encoding similarity: {avg_similarity:.4f}")
        
        # Save detailed results to CSV
        encoding_csv = os.path.join(OUTPUT_DIR, 'encoding_results.csv')
        df_encoding.to_csv(encoding_csv, index=False)
        print(f"Detailed encoding results saved to {encoding_csv}")
        
        # Create bar chart of encoding times
        plt.figure(figsize=(12, 6))
        
        # Filter for successful encodings
        successful_df = df_encoding[df_encoding['original_success'] & df_encoding['optimized_success']]
        
        if not successful_df.empty:
            images = successful_df['image']
            original_times = successful_df['original_time']
            optimized_times = successful_df['optimized_time']
            
            x = np.arange(len(images))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(12, 6))
            rects1 = ax.bar(x - width/2, original_times, width, label='Original')
            rects2 = ax.bar(x + width/2, optimized_times, width, label='Optimized')
            
            ax.set_title('Face Encoding Time Comparison')
            ax.set_xlabel('Image')
            ax.set_ylabel('Time (ms)')
            ax.set_xticks(x)
            ax.set_xticklabels(images, rotation=45)
            ax.legend()
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            encoding_chart = os.path.join(OUTPUT_DIR, 'encoding_time_comparison.png')
            plt.savefig(encoding_chart)
            print(f"Encoding time comparison chart saved to {encoding_chart}")
    
    # Overall summary
    print("\n----- Overall Optimization Summary -----\n")
    
    if detection_results and encoding_results:
        # Calculate overall speedup
        detection_speedup = df_detection['speedup'].mean()
        encoding_speedup = df_encoding['speedup'].mean()
        overall_speedup = (detection_speedup + encoding_speedup) / 2
        
        print(f"Face Detection Speedup: {detection_speedup:.2f}x")
        print(f"Face Encoding Speedup: {encoding_speedup:.2f}x")
        print(f"Overall Speedup: {overall_speedup:.2f}x")
        
        # Calculate success rate changes
        detection_success_change = optimized_success_rate - original_success_rate
        encoding_success_change = optimized_success_rate - original_success_rate
        
        print(f"Face Detection Success Rate Change: {detection_success_change:+.2f}%")
        print(f"Face Encoding Success Rate Change: {encoding_success_change:+.2f}%")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    run_tests()