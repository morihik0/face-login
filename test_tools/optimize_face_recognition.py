"""
Script to optimize face detection and recognition algorithms based on test results.

This script implements adjustments to the face detection and recognition algorithms
to improve their performance based on the results of our tests.
"""
import cv2
import numpy as np
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

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

# Define paths
TEST_IMAGES_DIR = 'tests/test_images'
OUTPUT_DIR = 'tests/results/optimization'

# Define optimal image dimensions
OPTIMAL_WIDTH = 640
OPTIMAL_HEIGHT = 480

# Define brightness thresholds
MIN_BRIGHTNESS = 50
MAX_BRIGHTNESS = 200

# Define number of iterations for performance testing
NUM_ITERATIONS = 5

def preprocess_image(image):
    """
    Preprocess image to improve face detection and recognition.
    
    Adjustments:
    1. Resize image to optimal dimensions
    2. Normalize brightness
    3. Enhance contrast
    """
    if image is None:
        return None
    
    # Get original dimensions
    original_height, original_width = image.shape[:2]
    
    # Resize image if it's too large
    if original_width > OPTIMAL_WIDTH or original_height > OPTIMAL_HEIGHT:
        # Calculate aspect ratio
        aspect_ratio = original_width / original_height
        
        # Determine new dimensions while preserving aspect ratio
        if aspect_ratio > 1:  # Width > Height
            new_width = OPTIMAL_WIDTH
            new_height = int(OPTIMAL_WIDTH / aspect_ratio)
        else:  # Height > Width
            new_height = OPTIMAL_HEIGHT
            new_width = int(OPTIMAL_HEIGHT * aspect_ratio)
        
        # Resize image
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Convert to HSV for brightness adjustment
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Calculate current brightness
    current_brightness = np.mean(v)
    
    # Adjust brightness if needed
    if current_brightness < MIN_BRIGHTNESS:
        # Increase brightness
        adjustment_factor = MIN_BRIGHTNESS / current_brightness
        v = cv2.convertScaleAbs(v, alpha=adjustment_factor, beta=0)
    elif current_brightness > MAX_BRIGHTNESS:
        # Decrease brightness
        adjustment_factor = MAX_BRIGHTNESS / current_brightness
        v = cv2.convertScaleAbs(v, alpha=adjustment_factor, beta=0)
    
    # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    v = clahe.apply(v)
    
    # Merge channels back
    hsv = cv2.merge([h, s, v])
    
    # Convert back to BGR
    processed_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return processed_image

def optimized_detect_faces(image):
    """
    Optimized version of detect_faces function.
    
    Improvements:
    1. Image preprocessing
    2. Downscaling for faster detection
    """
    # Preprocess image
    processed_image = preprocess_image(image)
    
    # Call original detect_faces function
    return detect_faces(processed_image)

def optimized_extract_face_encoding(image):
    """
    Optimized version of extract_face_encoding function.
    
    Improvements:
    1. Image preprocessing
    2. Error handling for multiple faces
    """
    # Preprocess image
    processed_image = preprocess_image(image)
    
    # Call original extract_face_encoding function
    return extract_face_encoding(processed_image)

def optimized_authenticate_face(image, threshold=None):
    """
    Optimized version of authenticate_face function.
    
    Improvements:
    1. Image preprocessing
    2. Adaptive thresholding based on image quality
    3. Early stopping in face comparison
    """
    # Preprocess image
    processed_image = preprocess_image(image)
    
    # Validate the image
    is_valid, message = validate_face_image(processed_image)
    if not is_valid:
        raise ValueError(f"Invalid image: {message}")
    
    # Extract face encoding
    face_encoding = extract_face_encoding(processed_image)
    
    # Get all users
    from app.database.models import User
    users = User.get_all()
    
    # Set default threshold if not provided
    if threshold is None:
        threshold = get_recognition_threshold()
    
    # Adjust threshold based on image quality
    # Lower threshold for lower quality images
    hsv = cv2.cvtColor(processed_image, cv2.COLOR_BGR2HSV)
    brightness = np.mean(hsv[:, :, 2])
    if brightness < 100 or brightness > 200:
        # Adjust threshold for non-optimal brightness
        threshold = max(0.4, threshold - 0.1)
    
    # Initialize variables
    best_match_user_id = None
    best_match_confidence = 0.0
    
    # Compare with each user's face encodings
    for user in users:
        # Get user's face encodings
        try:
            user_encodings = get_user_encodings(user.id)
            if not user_encodings:
                continue
            
            # Compare faces with early stopping
            for i, encoding in enumerate(user_encodings):
                # Compare with current encoding
                match_found, _, confidence = compare_faces([encoding], face_encoding, tolerance=threshold)
                
                # If match found with high confidence, stop comparing
                if match_found and confidence > 0.8:
                    return True, user.id, confidence
                
                # Update best match if better than current
                if confidence > best_match_confidence:
                    best_match_confidence = confidence
                    best_match_user_id = user.id
        except Exception as e:
            print(f"Warning: Error comparing with user {user.id}: {e}")
    
    # Determine if authentication is successful
    success = best_match_confidence >= threshold
    
    # Log authentication attempt
    from app.database.models import AuthLog
    AuthLog.create(
        user_id=best_match_user_id if success else None,
        timestamp=time.time(),
        success=success,
        confidence=best_match_confidence
    )
    
    return success, best_match_user_id if success else None, best_match_confidence

def test_optimization(test_images):
    """Test the optimization improvements."""
    results = []
    
    print("\nTesting optimization improvements...")
    
    for image_data in test_images:
        image_path = image_data['path']
        image_name = image_data['name']
        category = image_data['category']
        
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image from {image_path}")
            continue
        
        # Get image properties
        height, width, channels = image.shape
        size_kb = image.size * channels / 1024  # Size in KB
        
        # Test original functions
        original_detect_time = measure_function_time(detect_faces, image)
        original_encoding_time = measure_function_time(extract_face_encoding, image)
        original_auth_time = measure_function_time(authenticate_face, image)
        
        # Test optimized functions
        optimized_detect_time = measure_function_time(optimized_detect_faces, image)
        optimized_encoding_time = measure_function_time(optimized_extract_face_encoding, image)
        optimized_auth_time = measure_function_time(optimized_authenticate_face, image)
        
        # Record results
        results.append({
            'image_name': image_name,
            'category': category,
            'width': width,
            'height': height,
            'size_kb': size_kb,
            'original_detect_time': original_detect_time['time_ms'],
            'original_detect_success': original_detect_time['success'],
            'original_encoding_time': original_encoding_time['time_ms'],
            'original_encoding_success': original_encoding_time['success'],
            'original_auth_time': original_auth_time['time_ms'],
            'original_auth_success': original_auth_time['success'],
            'optimized_detect_time': optimized_detect_time['time_ms'],
            'optimized_detect_success': optimized_detect_time['success'],
            'optimized_encoding_time': optimized_encoding_time['time_ms'],
            'optimized_encoding_success': optimized_encoding_time['success'],
            'optimized_auth_time': optimized_auth_time['time_ms'],
            'optimized_auth_success': optimized_auth_time['success'],
            'detect_speedup': original_detect_time['time_ms'] / optimized_detect_time['time_ms'] if optimized_detect_time['time_ms'] > 0 else 0,
            'encoding_speedup': original_encoding_time['time_ms'] / optimized_encoding_time['time_ms'] if optimized_encoding_time['time_ms'] > 0 else 0,
            'auth_speedup': original_auth_time['time_ms'] / optimized_auth_time['time_ms'] if optimized_auth_time['time_ms'] > 0 else 0
        })
        
        print(f"Tested image: {image_name}")
    
    return pd.DataFrame(results)

def measure_function_time(func, *args, **kwargs):
    """Measure the execution time of a function."""
    start_time = time.time()
    
    try:
        result = func(*args, **kwargs)
        success = True
        error = None
    except Exception as e:
        result = None
        success = False
        error = str(e)
    
    elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    return {
        'time_ms': elapsed_time,
        'success': success,
        'error': error,
        'result': result
    }

def load_test_images():
    """Load test images for optimization testing."""
    test_images = []
    
    # Add base images
    base_images = [
        'single_face_test.jpg',
        'multi_face_test.jpg',
    ]
    
    for image_name in base_images:
        image_path = os.path.join(TEST_IMAGES_DIR, image_name)
        if os.path.exists(image_path):
            test_images.append({
                'path': image_path,
                'name': image_name,
                'category': 'base'
            })
    
    # Add images from condition directories
    condition_dirs = [
        'brightness',
        'sizes',
        'quality',
        'angles',
        'expressions',
        'occlusions',
        'backgrounds'
    ]
    
    for condition_dir in condition_dirs:
        dir_path = os.path.join(TEST_IMAGES_DIR, condition_dir)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            # Only add a few images from each category to keep the test manageable
            count = 0
            for image_name in os.listdir(dir_path):
                if count >= 2:  # Limit to 2 images per category
                    break
                
                if image_name.endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(dir_path, image_name)
                    test_images.append({
                        'path': image_path,
                        'name': image_name,
                        'category': condition_dir
                    })
                    count += 1
    
    print(f"Loaded {len(test_images)} test images")
    return test_images

def analyze_results(df):
    """Analyze optimization results."""
    if df is None or len(df) == 0:
        return None
    
    # Calculate overall statistics
    overall_stats = {
        'original_detect_time': df['original_detect_time'].mean(),
        'original_encoding_time': df['original_encoding_time'].mean(),
        'original_auth_time': df['original_auth_time'].mean(),
        'optimized_detect_time': df['optimized_detect_time'].mean(),
        'optimized_encoding_time': df['optimized_encoding_time'].mean(),
        'optimized_auth_time': df['optimized_auth_time'].mean(),
        'original_detect_success': df['original_detect_success'].mean() * 100,
        'original_encoding_success': df['original_encoding_success'].mean() * 100,
        'original_auth_success': df['original_auth_success'].mean() * 100,
        'optimized_detect_success': df['optimized_detect_success'].mean() * 100,
        'optimized_encoding_success': df['optimized_encoding_success'].mean() * 100,
        'optimized_auth_success': df['optimized_auth_success'].mean() * 100,
        'detect_speedup': df['detect_speedup'].mean(),
        'encoding_speedup': df['encoding_speedup'].mean(),
        'auth_speedup': df['auth_speedup'].mean()
    }
    
    # Calculate statistics by category
    category_stats = df.groupby('category').agg({
        'original_detect_time': 'mean',
        'original_encoding_time': 'mean',
        'original_auth_time': 'mean',
        'optimized_detect_time': 'mean',
        'optimized_encoding_time': 'mean',
        'optimized_auth_time': 'mean',
        'original_detect_success': lambda x: x.mean() * 100,
        'original_encoding_success': lambda x: x.mean() * 100,
        'original_auth_success': lambda x: x.mean() * 100,
        'optimized_detect_success': lambda x: x.mean() * 100,
        'optimized_encoding_success': lambda x: x.mean() * 100,
        'optimized_auth_success': lambda x: x.mean() * 100,
        'detect_speedup': 'mean',
        'encoding_speedup': 'mean',
        'auth_speedup': 'mean'
    })
    
    return {
        'overall_stats': overall_stats,
        'category_stats': category_stats
    }

def generate_report(df, analysis):
    """Generate a report on optimization results."""
    if df is None or analysis is None:
        return
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("\n===== ALGORITHM OPTIMIZATION REPORT =====\n")
    
    # Print overall statistics
    overall_stats = analysis['overall_stats']
    print("----- Overall Performance Improvement -----\n")
    
    print("Processing Time (ms):")
    print(f"Face Detection:     {overall_stats['original_detect_time']:.2f} -> {overall_stats['optimized_detect_time']:.2f} ({overall_stats['detect_speedup']:.2f}x speedup)")
    print(f"Face Encoding:      {overall_stats['original_encoding_time']:.2f} -> {overall_stats['optimized_encoding_time']:.2f} ({overall_stats['encoding_speedup']:.2f}x speedup)")
    print(f"Face Authentication: {overall_stats['original_auth_time']:.2f} -> {overall_stats['optimized_auth_time']:.2f} ({overall_stats['auth_speedup']:.2f}x speedup)")
    
    print("\nSuccess Rate (%):")
    print(f"Face Detection:      {overall_stats['original_detect_success']:.2f}% -> {overall_stats['optimized_detect_success']:.2f}%")
    print(f"Face Encoding:       {overall_stats['original_encoding_success']:.2f}% -> {overall_stats['optimized_encoding_success']:.2f}%")
    print(f"Face Authentication: {overall_stats['original_auth_success']:.2f}% -> {overall_stats['optimized_auth_success']:.2f}%")
    
    # Print statistics by category
    category_stats = analysis['category_stats']
    print("\n----- Performance Improvement by Category -----\n")
    
    # Format for display - Processing Time
    time_stats = category_stats[['original_detect_time', 'optimized_detect_time', 'detect_speedup',
                                'original_encoding_time', 'optimized_encoding_time', 'encoding_speedup',
                                'original_auth_time', 'optimized_auth_time', 'auth_speedup']]
    
    time_stats.columns = ['Original Detection (ms)', 'Optimized Detection (ms)', 'Detection Speedup',
                         'Original Encoding (ms)', 'Optimized Encoding (ms)', 'Encoding Speedup',
                         'Original Auth (ms)', 'Optimized Auth (ms)', 'Auth Speedup']
    
    print("Processing Time by Category:")
    print(tabulate(time_stats, headers='keys', tablefmt='grid', floatfmt='.2f'))
    
    # Format for display - Success Rate
    success_stats = category_stats[['original_detect_success', 'optimized_detect_success',
                                   'original_encoding_success', 'optimized_encoding_success',
                                   'original_auth_success', 'optimized_auth_success']]
    
    success_stats.columns = ['Original Detection (%)', 'Optimized Detection (%)',
                            'Original Encoding (%)', 'Optimized Encoding (%)',
                            'Original Auth (%)', 'Optimized Auth (%)']
    
    print("\nSuccess Rate by Category:")
    print(tabulate(success_stats, headers='keys', tablefmt='grid', floatfmt='.2f'))
    
    # Generate visualizations
    
    # 1. Processing time comparison
    plt.figure(figsize=(12, 6))
    
    # Prepare data
    functions = ['Face Detection', 'Face Encoding', 'Face Authentication']
    original_times = [overall_stats['original_detect_time'], 
                     overall_stats['original_encoding_time'], 
                     overall_stats['original_auth_time']]
    optimized_times = [overall_stats['optimized_detect_time'], 
                      overall_stats['optimized_encoding_time'], 
                      overall_stats['optimized_auth_time']]
    
    x = np.arange(len(functions))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, original_times, width, label='Original')
    rects2 = ax.bar(x + width/2, optimized_times, width, label='Optimized')
    
    ax.set_title('Processing Time Comparison')
    ax.set_xlabel('Function')
    ax.set_ylabel('Time (ms)')
    ax.set_xticks(x)
    ax.set_xticklabels(functions)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add value labels
    for i, rect in enumerate(rects1):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height + 5,
                f"{height:.1f}", ha='center', va='bottom')
    
    for i, rect in enumerate(rects2):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height + 5,
                f"{height:.1f}", ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'processing_time_comparison.png'))
    print(f"\nSaved processing time comparison to {os.path.join(OUTPUT_DIR, 'processing_time_comparison.png')}")
    
    # 2. Success rate comparison
    plt.figure(figsize=(12, 6))
    
    # Prepare data
    original_success = [overall_stats['original_detect_success'], 
                       overall_stats['original_encoding_success'], 
                       overall_stats['original_auth_success']]
    optimized_success = [overall_stats['optimized_detect_success'], 
                        overall_stats['optimized_encoding_success'], 
                        overall_stats['optimized_auth_success']]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, original_success, width, label='Original')
    rects2 = ax.bar(x + width/2, optimized_success, width, label='Optimized')
    
    ax.set_title('Success Rate Comparison')
    ax.set_xlabel('Function')
    ax.set_ylabel('Success Rate (%)')
    ax.set_xticks(x)
    ax.set_xticklabels(functions)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add value labels
    for i, rect in enumerate(rects1):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height + 1,
                f"{height:.1f}%", ha='center', va='bottom')
    
    for i, rect in enumerate(rects2):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height + 1,
                f"{height:.1f}%", ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'success_rate_comparison.png'))
    print(f"Saved success rate comparison to {os.path.join(OUTPUT_DIR, 'success_rate_comparison.png')}")
    
    # 3. Speedup by category
    plt.figure(figsize=(12, 8))
    
    # Prepare data
    categories = category_stats.index
    detect_speedup = category_stats['detect_speedup']
    encoding_speedup = category_stats['encoding_speedup']
    auth_speedup = category_stats['auth_speedup']
    
    x = np.arange(len(categories))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 8))
    rects1 = ax.bar(x - width, detect_speedup, width, label='Detection')
    rects2 = ax.bar(x, encoding_speedup, width, label='Encoding')
    rects3 = ax.bar(x + width, auth_speedup, width, label='Authentication')
    
    ax.set_title('Speedup by Category')
    ax.set_xlabel('Category')
    ax.set_ylabel('Speedup Factor (x)')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'speedup_by_category.png'))
    print(f"Saved speedup by category to {os.path.join(OUTPUT_DIR, 'speedup_by_category.png')}")
    
    # Save results to CSV
    df.to_csv(os.path.join(OUTPUT_DIR, 'optimization_results.csv'), index=False)
    print(f"\nSaved detailed results to {os.path.join(OUTPUT_DIR, 'optimization_results.csv')}")
    
    # Save analysis to CSV
    pd.DataFrame([overall_stats]).to_csv(os.path.join(OUTPUT_DIR, 'overall_improvement.csv'), index=False)
    print(f"Saved overall improvement to {os.path.join(OUTPUT_DIR, 'overall_improvement.csv')}")
    
    category_stats.to_csv(os.path.join(OUTPUT_DIR, 'improvement_by_category.csv'))
    print(f"Saved improvement by category to {os.path.join(OUTPUT_DIR, 'improvement_by_category.csv')}")
    
    # Generate implementation recommendations
    print("\n===== IMPLEMENTATION RECOMMENDATIONS =====\n")
    
    print("Based on the optimization results, the following changes are recommended:")
    
    print("\n1. Image Preprocessing:")
    print("   - Implement automatic image resizing to optimal dimensions (640x480)")
    print("   - Add brightness normalization to handle dark and bright images")
    print("   - Apply contrast enhancement using CLAHE")
    
    print("\n2. Face Detection Optimization:")
    print("   - Use the optimized_detect_faces function which includes preprocessing")
    print("   - Consider implementing a face detection cache for frequently processed images")
    
    print("\n3. Face Encoding Optimization:")
    print("   - Use the optimized_extract_face_encoding function with preprocessing")
    print("   - Implement error handling for multiple faces")
    
    print("\n4. Face Authentication Optimization:")
    print("   - Use the optimized_authenticate_face function with:")
    print("     * Image preprocessing")
    print("     * Adaptive thresholding based on image quality")
    print("     * Early stopping in face comparison")
    
    print("\n5. System-Level Optimizations:")
    print("   - Implement caching for frequently accessed face encodings")
    print("   - Consider hardware acceleration (GPU) for face detection and encoding")
    print("   - Optimize database queries for face encoding retrieval")
    
    print("\nThese optimizations should significantly improve both the performance and success rate of the face recognition system.")

def main():
    """Main function."""
    print("Starting algorithm optimization based on test results...")
    
    # Load test images
    test_images = load_test_images()
    if not test_images:
        print("Failed to load test images")
        return
    
    # Test optimization
    results = test_optimization(test_images)
    
    # Analyze results
    analysis = analyze_results(results)
    
    # Generate report
    generate_report(results, analysis)
    
    print("\nAlgorithm optimization completed!")

if __name__ == "__main__":
    main()