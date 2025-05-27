"""
Test script for face authentication accuracy.

This script tests the accuracy of the face authentication system by:
1. Registering test users with face images
2. Testing authentication with various test images
3. Calculating authentication accuracy metrics
4. Generating a report on authentication accuracy
"""
import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
from datetime import datetime
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc

from app.database.db import init_db, get_db_connection
from app.database.models import User, FaceEncoding, AuthLog
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
    set_recognition_threshold
)

# Define paths
TEST_IMAGES_DIR = 'tests/test_images'
OUTPUT_DIR = 'tests/results/authentication'

# Test users data
TEST_USERS = [
    {"name": "Test User 1", "email": "user1@example.com", "image": "single_face_test.jpg"},
    {"name": "Test User 2", "email": "user2@example.com", "image": "test_face.jpg"},
]

# Test thresholds
TEST_THRESHOLDS = [0.4, 0.5, 0.6, 0.7, 0.8]

def setup_test_environment():
    """Set up the test environment by initializing the database and creating test users."""
    print("Setting up test environment...")
    
    # Initialize database
    if not init_db():
        print("Failed to initialize database")
        return None
    
    # Create test directory for face images
    os.makedirs('face_images', exist_ok=True)
    
    # Create test users
    created_users = []
    for user_data in TEST_USERS:
        try:
            # Check if user already exists
            user = User.get_by_email(user_data["email"])
            if user:
                print(f"User {user_data['name']} already exists with ID: {user.id}")
                created_users.append(user)
            else:
                # Create new user
                user = User.create(user_data["name"], user_data["email"])
                print(f"Created user {user.name} with ID: {user.id}")
                created_users.append(user)
        except Exception as e:
            print(f"Error creating user {user_data['name']}: {e}")
    
    return created_users

def register_test_faces(users):
    """Register test faces for the given users."""
    print("\nRegistering test faces...")
    
    registered_faces = []
    
    for i, user in enumerate(users):
        if i < len(TEST_USERS):
            image_path = os.path.join(TEST_IMAGES_DIR, TEST_USERS[i]["image"])
            
            if not os.path.exists(image_path):
                print(f"Error: Test image not found at {image_path}")
                continue
            
            try:
                # Load the image
                image = cv2.imread(image_path)
                if image is None:
                    print(f"Error: Could not read image from {image_path}")
                    continue
                
                print(f"Registering face for {user.name} (ID: {user.id})...")
                
                # Check if user already has registered faces
                existing_faces = FaceEncoding.get_by_user_id(user.id)
                if existing_faces and len(existing_faces) > 0:
                    print(f"User {user.name} already has {len(existing_faces)} registered faces")
                    registered_faces.append({
                        "user": user,
                        "image_path": image_path,
                        "encoding_id": existing_faces[0].id
                    })
                    continue
                
                # Register the face
                face_encoding = register_face(user.id, image)
                print(f"Face registered successfully with ID: {face_encoding.id}")
                registered_faces.append({
                    "user": user,
                    "image_path": image_path,
                    "encoding_id": face_encoding.id
                })
            except Exception as e:
                print(f"Error registering face for {user.name}: {e}")
    
    return registered_faces

def prepare_test_images():
    """Prepare test images for authentication testing."""
    print("\nPreparing test images...")
    
    test_images = []
    
    # Add base images
    base_images = [
        'single_face_test.jpg',
        'test_face.jpg',
    ]
    
    for image_name in base_images:
        image_path = os.path.join(TEST_IMAGES_DIR, image_name)
        if os.path.exists(image_path):
            test_images.append({
                'path': image_path,
                'name': image_name,
                'category': 'base',
                'expected_user': 0 if image_name == 'single_face_test.jpg' else 1
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
            for image_name in os.listdir(dir_path):
                if image_name.endswith(('.jpg', '.jpeg', '.png')):
                    # Determine expected user based on image name
                    expected_user = None
                    if 'single_face_test' in image_name:
                        expected_user = 0
                    elif 'test_face' in image_name:
                        expected_user = 1
                    else:
                        continue  # Skip images not related to our test users
                    
                    test_images.append({
                        'path': os.path.join(dir_path, image_name),
                        'name': image_name,
                        'category': condition_dir,
                        'expected_user': expected_user
                    })
    
    print(f"Prepared {len(test_images)} test images")
    return test_images

def test_authentication(registered_users, test_images, threshold=None):
    """Test face authentication with the given test images."""
    print(f"\nTesting authentication with threshold: {threshold if threshold else 'default'}")
    
    if threshold is not None:
        set_recognition_threshold(threshold)
    
    current_threshold = get_recognition_threshold()
    print(f"Current threshold: {current_threshold}")
    
    results = []
    
    for image_data in test_images:
        image_path = image_data['path']
        expected_user_idx = image_data['expected_user']
        expected_user = registered_users[expected_user_idx] if expected_user_idx < len(registered_users) else None
        
        print(f"Testing with image: {image_data['name']}")
        
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image from {image_path}")
            continue
        
        try:
            # Authenticate the face
            success, user_id, confidence = authenticate_face(image)
            
            # Determine if this is a true positive, false positive, etc.
            if expected_user is not None:
                expected_user_id = expected_user.id
                true_positive = success and user_id == expected_user_id
                false_negative = not success and expected_user_id is not None
                false_positive = success and user_id != expected_user_id
                true_negative = not success and expected_user_id is None
            else:
                expected_user_id = None
                true_positive = False
                false_negative = False
                false_positive = success
                true_negative = not success
            
            # Record the result
            results.append({
                'image_name': image_data['name'],
                'category': image_data['category'],
                'expected_user_id': expected_user_id,
                'authenticated_user_id': user_id,
                'success': success,
                'confidence': confidence,
                'true_positive': true_positive,
                'false_negative': false_negative,
                'false_positive': false_positive,
                'true_negative': true_negative,
                'threshold': current_threshold
            })
            
            # Print result
            if success:
                authenticated_user = User.get_by_id(user_id)
                print(f"Authentication successful! User: {authenticated_user.name}, Confidence: {confidence:.2f}")
                if expected_user_id is not None and user_id != expected_user_id:
                    print(f"WARNING: Expected user {expected_user.name} but authenticated as {authenticated_user.name}")
            else:
                print(f"Authentication failed. Confidence: {confidence:.2f}")
                if expected_user_id is not None:
                    print(f"WARNING: Expected to authenticate user {expected_user.name}")
            
        except Exception as e:
            print(f"Error during authentication: {e}")
            
            # Record the error
            results.append({
                'image_name': image_data['name'],
                'category': image_data['category'],
                'expected_user_id': expected_user_id if expected_user else None,
                'authenticated_user_id': None,
                'success': False,
                'confidence': 0.0,
                'true_positive': False,
                'false_negative': expected_user is not None,
                'false_positive': False,
                'true_negative': expected_user is None,
                'threshold': current_threshold,
                'error': str(e)
            })
    
    return results

def calculate_metrics(results):
    """Calculate authentication accuracy metrics."""
    if not results:
        return None
    
    # Convert results to DataFrame
    df = pd.DataFrame(results)
    
    # Calculate metrics
    total = len(df)
    true_positives = df['true_positive'].sum()
    false_positives = df['false_positive'].sum()
    true_negatives = df['true_negative'].sum()
    false_negatives = df['false_negative'].sum()
    
    accuracy = (true_positives + true_negatives) / total if total > 0 else 0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    metrics = {
        'threshold': df['threshold'].iloc[0],
        'total': total,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'true_negatives': true_negatives,
        'false_negatives': false_negatives,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    }
    
    return metrics

def generate_report(all_results, all_metrics):
    """Generate a report from the test results."""
    if not all_results or not all_metrics:
        return
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Combine all results
    df_results = pd.concat([pd.DataFrame(results) for results in all_results])
    
    # Convert metrics to DataFrame
    df_metrics = pd.DataFrame(all_metrics)
    
    print("\n===== FACE AUTHENTICATION ACCURACY REPORT =====\n")
    
    # Print metrics for each threshold
    print("----- Authentication Metrics by Threshold -----\n")
    metrics_table = df_metrics[['threshold', 'accuracy', 'precision', 'recall', 'f1_score']]
    metrics_table = metrics_table.sort_values('threshold')
    metrics_table[['accuracy', 'precision', 'recall', 'f1_score']] *= 100  # Convert to percentage
    print(tabulate(metrics_table, headers='keys', tablefmt='grid', floatfmt='.2f'))
    
    # Find the best threshold based on F1 score
    best_threshold_idx = df_metrics['f1_score'].idxmax()
    best_threshold = df_metrics.loc[best_threshold_idx, 'threshold']
    best_f1 = df_metrics.loc[best_threshold_idx, 'f1_score'] * 100
    
    print(f"\nBest threshold based on F1 score: {best_threshold} (F1 = {best_f1:.2f}%)")
    
    # Print confusion matrix for the best threshold
    best_results = all_results[best_threshold_idx]
    df_best = pd.DataFrame(best_results)
    
    print("\n----- Confusion Matrix for Best Threshold -----\n")
    y_true = df_best['expected_user_id'].notna()  # True if expected user exists
    y_pred = df_best['success']  # True if authentication succeeded
    
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    print(f"True Positives: {tp}")
    print(f"False Positives: {fp}")
    print(f"True Negatives: {tn}")
    print(f"False Negatives: {fn}")
    
    # Calculate metrics by category for the best threshold
    print("\n----- Authentication Accuracy by Category -----\n")
    category_metrics = df_best.groupby('category').apply(lambda x: pd.Series({
        'total': len(x),
        'true_positives': x['true_positive'].sum(),
        'false_positives': x['false_positive'].sum(),
        'true_negatives': x['true_negative'].sum(),
        'false_negatives': x['false_negative'].sum(),
        'accuracy': (x['true_positive'].sum() + x['true_negative'].sum()) / len(x) * 100,
    }))
    
    print(tabulate(category_metrics.sort_values('accuracy', ascending=False), 
                  headers='keys', tablefmt='grid', floatfmt='.2f'))
    
    # Generate visualizations
    
    # 1. ROC Curve
    plt.figure(figsize=(10, 6))
    
    # Prepare data for ROC curve
    thresholds = []
    tpr_list = []
    fpr_list = []
    
    for metrics in all_metrics:
        threshold = metrics['threshold']
        tpr = metrics['recall']  # True Positive Rate = Recall
        fpr = metrics['false_positives'] / (metrics['false_positives'] + metrics['true_negatives']) if (metrics['false_positives'] + metrics['true_negatives']) > 0 else 0
        
        thresholds.append(threshold)
        tpr_list.append(tpr)
        fpr_list.append(fpr)
    
    # Sort by threshold
    sorted_indices = np.argsort(thresholds)
    thresholds = [thresholds[i] for i in sorted_indices]
    tpr_list = [tpr_list[i] for i in sorted_indices]
    fpr_list = [fpr_list[i] for i in sorted_indices]
    
    # Calculate AUC
    roc_auc = auc(fpr_list, tpr_list)
    
    # Plot ROC curve
    plt.plot(fpr_list, tpr_list, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc="lower right")
    
    # Add threshold annotations
    for i, threshold in enumerate(thresholds):
        plt.annotate(f"{threshold}", (fpr_list[i], tpr_list[i]), textcoords="offset points", xytext=(0,10), ha='center')
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'roc_curve.png'))
    print(f"Saved ROC curve to {os.path.join(OUTPUT_DIR, 'roc_curve.png')}")
    
    # 2. Metrics vs Threshold
    plt.figure(figsize=(12, 6))
    
    # Sort metrics by threshold
    df_metrics_sorted = df_metrics.sort_values('threshold')
    
    # Plot metrics
    plt.plot(df_metrics_sorted['threshold'], df_metrics_sorted['accuracy'] * 100, 'o-', label='Accuracy')
    plt.plot(df_metrics_sorted['threshold'], df_metrics_sorted['precision'] * 100, 'o-', label='Precision')
    plt.plot(df_metrics_sorted['threshold'], df_metrics_sorted['recall'] * 100, 'o-', label='Recall')
    plt.plot(df_metrics_sorted['threshold'], df_metrics_sorted['f1_score'] * 100, 'o-', label='F1 Score')
    
    plt.axvline(x=best_threshold, color='r', linestyle='--', label=f'Best Threshold ({best_threshold})')
    
    plt.xlabel('Threshold')
    plt.ylabel('Percentage (%)')
    plt.title('Authentication Metrics vs Threshold')
    plt.legend()
    plt.grid(True)
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'metrics_vs_threshold.png'))
    print(f"Saved metrics plot to {os.path.join(OUTPUT_DIR, 'metrics_vs_threshold.png')}")
    
    # 3. Category Accuracy Bar Chart
    plt.figure(figsize=(12, 6))
    
    # Sort by accuracy
    category_metrics_sorted = category_metrics.sort_values('accuracy', ascending=False)
    
    # Plot bar chart
    ax = sns.barplot(x=category_metrics_sorted.index, y=category_metrics_sorted['accuracy'])
    plt.title('Authentication Accuracy by Category')
    plt.xlabel('Category')
    plt.ylabel('Accuracy (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Add value labels on bars
    for i, v in enumerate(category_metrics_sorted['accuracy']):
        ax.text(i, v + 1, f"{v:.1f}%", ha='center')
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'accuracy_by_category.png'))
    print(f"Saved category accuracy plot to {os.path.join(OUTPUT_DIR, 'accuracy_by_category.png')}")
    
    # Save results to CSV
    df_results.to_csv(os.path.join(OUTPUT_DIR, 'authentication_test_results.csv'), index=False)
    print(f"Saved detailed results to {os.path.join(OUTPUT_DIR, 'authentication_test_results.csv')}")
    
    df_metrics.to_csv(os.path.join(OUTPUT_DIR, 'authentication_metrics.csv'), index=False)
    print(f"Saved metrics to {os.path.join(OUTPUT_DIR, 'authentication_metrics.csv')}")
    
    category_metrics.to_csv(os.path.join(OUTPUT_DIR, 'authentication_category_metrics.csv'))
    print(f"Saved category metrics to {os.path.join(OUTPUT_DIR, 'authentication_category_metrics.csv')}")

def main():
    """Main function."""
    print("Starting face authentication accuracy tests...")
    
    # Setup test environment
    users = setup_test_environment()
    if not users:
        print("Failed to set up test environment")
        return
    
    # Register test faces
    registered_faces = register_test_faces(users)
    if not registered_faces:
        print("Failed to register test faces")
        return
    
    # Prepare test images
    test_images = prepare_test_images()
    if not test_images:
        print("Failed to prepare test images")
        return
    
    # Test authentication with different thresholds
    all_results = []
    all_metrics = []
    
    for threshold in TEST_THRESHOLDS:
        results = test_authentication(users, test_images, threshold)
        metrics = calculate_metrics(results)
        
        all_results.append(results)
        all_metrics.append(metrics)
    
    # Generate report
    generate_report(all_results, all_metrics)
    
    # Reset threshold to default
    set_recognition_threshold(0.6)
    print(f"Reset threshold to default: {get_recognition_threshold()}")
    
    print("\nFace authentication accuracy tests completed!")

if __name__ == "__main__":
    main()