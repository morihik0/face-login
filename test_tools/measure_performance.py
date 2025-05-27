"""
Script to measure the performance (processing time) of face detection and recognition functions.

This script measures the processing time of key functions and analyzes how different factors
affect performance, identifying bottlenecks and providing recommendations for improvement.
"""
import cv2
import numpy as np
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
    get_user_encodings,
    compare_faces
)

# Define paths
TEST_IMAGES_DIR = 'tests/test_images'
OUTPUT_DIR = 'tests/results/performance'

# Define number of iterations for each test
NUM_ITERATIONS = 10

def load_test_images():
    """Load test images for performance measurement."""
    test_images = []
    
    # Add base images
    base_images = [
        'single_face_test.jpg',
        'multi_face_test.jpg',
    ]
    
    for image_name in base_images:
        image_path = os.path.join(TEST_IMAGES_DIR, image_name)
        if os.path.exists(image_path):
            image = cv2.imread(image_path)
            if image is not None:
                test_images.append({
                    'path': image_path,
                    'name': image_name,
                    'category': 'base',
                    'image': image
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
                    image = cv2.imread(image_path)
                    
                    if image is not None:
                        test_images.append({
                            'path': image_path,
                            'name': image_name,
                            'category': condition_dir,
                            'image': image
                        })
                        count += 1
    
    print(f"Loaded {len(test_images)} test images")
    return test_images

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

def measure_detect_faces(image, iterations=1):
    """Measure the performance of detect_faces function."""
    times = []
    success_count = 0
    
    for _ in range(iterations):
        result = measure_function_time(detect_faces, image)
        times.append(result['time_ms'])
        if result['success']:
            success_count += 1
    
    return {
        'avg_time_ms': np.mean(times),
        'min_time_ms': np.min(times),
        'max_time_ms': np.max(times),
        'std_time_ms': np.std(times),
        'success_rate': success_count / iterations * 100
    }

def measure_extract_face_encoding(image, iterations=1):
    """Measure the performance of extract_face_encoding function."""
    times = []
    success_count = 0
    
    for _ in range(iterations):
        result = measure_function_time(extract_face_encoding, image)
        times.append(result['time_ms'])
        if result['success']:
            success_count += 1
    
    return {
        'avg_time_ms': np.mean(times),
        'min_time_ms': np.min(times),
        'max_time_ms': np.max(times),
        'std_time_ms': np.std(times),
        'success_rate': success_count / iterations * 100
    }

def measure_authenticate_face(image, iterations=1):
    """Measure the performance of authenticate_face function."""
    times = []
    success_count = 0
    
    for _ in range(iterations):
        result = measure_function_time(authenticate_face, image)
        times.append(result['time_ms'])
        if result['success'] and result['result'][0]:  # Check if authentication succeeded
            success_count += 1
    
    return {
        'avg_time_ms': np.mean(times),
        'min_time_ms': np.min(times),
        'max_time_ms': np.max(times),
        'std_time_ms': np.std(times),
        'success_rate': success_count / iterations * 100
    }

def measure_performance(test_images):
    """Measure the performance of face detection and recognition functions."""
    results = []
    
    print("\nMeasuring performance...")
    
    for image_data in tqdm(test_images, desc="Processing images"):
        image = image_data['image']
        image_name = image_data['name']
        category = image_data['category']
        
        # Get image properties
        height, width, channels = image.shape
        size_kb = image.size * channels / 1024  # Size in KB
        
        # Measure detect_faces performance
        detect_perf = measure_detect_faces(image, NUM_ITERATIONS)
        
        # Measure extract_face_encoding performance
        encoding_perf = measure_extract_face_encoding(image, NUM_ITERATIONS)
        
        # Measure authenticate_face performance
        auth_perf = measure_authenticate_face(image, NUM_ITERATIONS)
        
        # Record results
        results.append({
            'image_name': image_name,
            'category': category,
            'width': width,
            'height': height,
            'size_kb': size_kb,
            'detect_avg_time_ms': detect_perf['avg_time_ms'],
            'detect_min_time_ms': detect_perf['min_time_ms'],
            'detect_max_time_ms': detect_perf['max_time_ms'],
            'detect_std_time_ms': detect_perf['std_time_ms'],
            'detect_success_rate': detect_perf['success_rate'],
            'encoding_avg_time_ms': encoding_perf['avg_time_ms'],
            'encoding_min_time_ms': encoding_perf['min_time_ms'],
            'encoding_max_time_ms': encoding_perf['max_time_ms'],
            'encoding_std_time_ms': encoding_perf['std_time_ms'],
            'encoding_success_rate': encoding_perf['success_rate'],
            'auth_avg_time_ms': auth_perf['avg_time_ms'],
            'auth_min_time_ms': auth_perf['min_time_ms'],
            'auth_max_time_ms': auth_perf['max_time_ms'],
            'auth_std_time_ms': auth_perf['std_time_ms'],
            'auth_success_rate': auth_perf['success_rate']
        })
    
    return pd.DataFrame(results)

def analyze_performance(df):
    """Analyze performance results."""
    if df is None or len(df) == 0:
        return None
    
    # Calculate overall statistics
    overall_stats = {
        'detect_avg_time_ms': df['detect_avg_time_ms'].mean(),
        'encoding_avg_time_ms': df['encoding_avg_time_ms'].mean(),
        'auth_avg_time_ms': df['auth_avg_time_ms'].mean(),
        'detect_success_rate': df['detect_success_rate'].mean(),
        'encoding_success_rate': df['encoding_success_rate'].mean(),
        'auth_success_rate': df['auth_success_rate'].mean()
    }
    
    # Calculate statistics by category
    category_stats = df.groupby('category').agg({
        'detect_avg_time_ms': 'mean',
        'encoding_avg_time_ms': 'mean',
        'auth_avg_time_ms': 'mean',
        'detect_success_rate': 'mean',
        'encoding_success_rate': 'mean',
        'auth_success_rate': 'mean'
    })
    
    # Analyze correlation between image properties and performance
    correlation = df[['width', 'height', 'size_kb', 
                      'detect_avg_time_ms', 'encoding_avg_time_ms', 'auth_avg_time_ms']].corr()
    
    return {
        'overall_stats': overall_stats,
        'category_stats': category_stats,
        'correlation': correlation
    }

def generate_report(df, analysis):
    """Generate a report on performance measurements."""
    if df is None or analysis is None:
        return
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("\n===== PERFORMANCE MEASUREMENT REPORT =====\n")
    
    # Print overall statistics
    overall_stats = analysis['overall_stats']
    print("----- Overall Performance Statistics -----\n")
    print(f"Face Detection Average Time: {overall_stats['detect_avg_time_ms']:.2f} ms")
    print(f"Face Encoding Average Time: {overall_stats['encoding_avg_time_ms']:.2f} ms")
    print(f"Face Authentication Average Time: {overall_stats['auth_avg_time_ms']:.2f} ms")
    print(f"Total Processing Time: {overall_stats['detect_avg_time_ms'] + overall_stats['encoding_avg_time_ms'] + overall_stats['auth_avg_time_ms']:.2f} ms")
    
    print(f"\nFace Detection Success Rate: {overall_stats['detect_success_rate']:.2f}%")
    print(f"Face Encoding Success Rate: {overall_stats['encoding_success_rate']:.2f}%")
    print(f"Face Authentication Success Rate: {overall_stats['auth_success_rate']:.2f}%")
    
    # Print statistics by category
    category_stats = analysis['category_stats']
    print("\n----- Performance by Category -----\n")
    
    # Format for display
    display_stats = category_stats.copy()
    display_stats.columns = ['Detection (ms)', 'Encoding (ms)', 'Authentication (ms)', 
                            'Detection Success (%)', 'Encoding Success (%)', 'Authentication Success (%)']
    
    print(tabulate(display_stats, headers='keys', tablefmt='grid', floatfmt='.2f'))
    
    # Print correlation analysis
    correlation = analysis['correlation']
    print("\n----- Correlation Between Image Properties and Performance -----\n")
    
    # Format correlation matrix for display
    corr_display = correlation.loc[['width', 'height', 'size_kb'], 
                                  ['detect_avg_time_ms', 'encoding_avg_time_ms', 'auth_avg_time_ms']]
    corr_display.columns = ['Detection Time', 'Encoding Time', 'Authentication Time']
    corr_display.index = ['Image Width', 'Image Height', 'Image Size (KB)']
    
    print(tabulate(corr_display, headers='keys', tablefmt='grid', floatfmt='.2f'))
    
    # Generate visualizations
    
    # 1. Processing time breakdown
    plt.figure(figsize=(10, 6))
    labels = ['Face Detection', 'Face Encoding', 'Face Authentication']
    times = [overall_stats['detect_avg_time_ms'], 
             overall_stats['encoding_avg_time_ms'], 
             overall_stats['auth_avg_time_ms']]
    
    plt.bar(labels, times)
    plt.title('Average Processing Time Breakdown')
    plt.xlabel('Processing Step')
    plt.ylabel('Time (ms)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add value labels on bars
    for i, v in enumerate(times):
        plt.text(i, v + 1, f"{v:.2f} ms", ha='center')
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'processing_time_breakdown.png'))
    print(f"\nSaved processing time breakdown to {os.path.join(OUTPUT_DIR, 'processing_time_breakdown.png')}")
    
    # 2. Processing time by category
    plt.figure(figsize=(12, 8))
    
    # Prepare data for grouped bar chart
    categories = category_stats.index
    detection_times = category_stats['detect_avg_time_ms']
    encoding_times = category_stats['encoding_avg_time_ms']
    auth_times = category_stats['auth_avg_time_ms']
    
    x = np.arange(len(categories))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(12, 8))
    rects1 = ax.bar(x - width, detection_times, width, label='Detection')
    rects2 = ax.bar(x, encoding_times, width, label='Encoding')
    rects3 = ax.bar(x + width, auth_times, width, label='Authentication')
    
    ax.set_title('Processing Time by Category')
    ax.set_xlabel('Category')
    ax.set_ylabel('Time (ms)')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'processing_time_by_category.png'))
    print(f"Saved processing time by category to {os.path.join(OUTPUT_DIR, 'processing_time_by_category.png')}")
    
    # 3. Correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title('Correlation Between Image Properties and Performance')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_heatmap.png'))
    print(f"Saved correlation heatmap to {os.path.join(OUTPUT_DIR, 'correlation_heatmap.png')}")
    
    # 4. Scatter plot of image size vs processing time
    plt.figure(figsize=(10, 6))
    plt.scatter(df['size_kb'], df['auth_avg_time_ms'])
    plt.title('Image Size vs Authentication Time')
    plt.xlabel('Image Size (KB)')
    plt.ylabel('Authentication Time (ms)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add trend line
    z = np.polyfit(df['size_kb'], df['auth_avg_time_ms'], 1)
    p = np.poly1d(z)
    plt.plot(df['size_kb'], p(df['size_kb']), "r--", alpha=0.8)
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'size_vs_time.png'))
    print(f"Saved size vs time plot to {os.path.join(OUTPUT_DIR, 'size_vs_time.png')}")
    
    # Save results to CSV
    df.to_csv(os.path.join(OUTPUT_DIR, 'performance_measurements.csv'), index=False)
    print(f"\nSaved detailed measurements to {os.path.join(OUTPUT_DIR, 'performance_measurements.csv')}")
    
    category_stats.to_csv(os.path.join(OUTPUT_DIR, 'performance_by_category.csv'))
    print(f"Saved category statistics to {os.path.join(OUTPUT_DIR, 'performance_by_category.csv')}")
    
    correlation.to_csv(os.path.join(OUTPUT_DIR, 'performance_correlation.csv'))
    print(f"Saved correlation analysis to {os.path.join(OUTPUT_DIR, 'performance_correlation.csv')}")
    
    # Generate recommendations
    print("\n===== PERFORMANCE OPTIMIZATION RECOMMENDATIONS =====\n")
    
    # Identify bottlenecks
    times = [overall_stats['detect_avg_time_ms'], 
             overall_stats['encoding_avg_time_ms'], 
             overall_stats['auth_avg_time_ms']]
    
    bottleneck_index = np.argmax(times)
    bottleneck_step = ['Face Detection', 'Face Encoding', 'Face Authentication'][bottleneck_index]
    bottleneck_time = times[bottleneck_index]
    total_time = sum(times)
    bottleneck_percentage = bottleneck_time / total_time * 100
    
    print(f"Performance Bottleneck: {bottleneck_step} ({bottleneck_time:.2f} ms, {bottleneck_percentage:.2f}% of total processing time)")
    
    # Recommendations based on bottleneck
    print("\nRecommendations for improving performance:")
    
    if bottleneck_index == 0:  # Face Detection
        print("1. Optimize Face Detection:")
        print("   - Implement image downscaling before detection")
        print("   - Use a faster face detection algorithm (e.g., MTCNN or RetinaFace)")
        print("   - Implement parallel processing for multi-face detection")
    elif bottleneck_index == 1:  # Face Encoding
        print("1. Optimize Face Encoding:")
        print("   - Use a lighter face encoding model")
        print("   - Implement caching for frequently processed faces")
        print("   - Consider hardware acceleration (GPU) for encoding")
    else:  # Face Authentication
        print("1. Optimize Face Authentication:")
        print("   - Implement indexing for faster face comparison")
        print("   - Reduce the number of reference encodings per user")
        print("   - Implement early stopping in face comparison")
    
    # General recommendations
    print("\n2. General Optimizations:")
    print("   - Implement image preprocessing to standardize inputs")
    print("   - Use batch processing for multiple images")
    print("   - Consider hardware acceleration (GPU) for all steps")
    print("   - Implement caching for frequently accessed data")
    
    # Recommendations based on correlation analysis
    if correlation.loc['size_kb', 'auth_avg_time_ms'] > 0.5:
        print("\n3. Image Size Optimization:")
        print("   - Implement automatic image resizing to reduce processing time")
        print("   - Set optimal image dimensions for face detection and recognition")
        print("   - Use image compression to reduce memory usage")

def main():
    """Main function."""
    print("Starting performance measurement...")
    
    # Load test images
    test_images = load_test_images()
    if not test_images:
        print("Failed to load test images")
        return
    
    # Measure performance
    results = measure_performance(test_images)
    
    # Analyze performance
    analysis = analyze_performance(results)
    
    # Generate report
    generate_report(results, analysis)
    
    print("\nPerformance measurement completed!")

if __name__ == "__main__":
    main()