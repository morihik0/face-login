"""
Script to analyze face detection rate from test results.

This script analyzes the face detection test results to measure detection rates
under different conditions and identify factors that affect detection performance.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

# Define paths
RESULTS_DIR = 'tests/results'
RESULTS_FILE = os.path.join(RESULTS_DIR, 'face_detection_test_results.csv')
SUMMARY_FILE = os.path.join(RESULTS_DIR, 'face_detection_test_summary.csv')
OUTPUT_DIR = os.path.join(RESULTS_DIR, 'analysis')

def load_results():
    """Load test results from CSV file."""
    if not os.path.exists(RESULTS_FILE):
        print(f"Error: Results file not found at {RESULTS_FILE}")
        return None
    
    try:
        df = pd.read_csv(RESULTS_FILE)
        print(f"Loaded {len(df)} test results")
        return df
    except Exception as e:
        print(f"Error loading results: {e}")
        return None

def analyze_detection_rate(df):
    """Analyze detection rate by different factors."""
    if df is None or len(df) == 0:
        return
    
    # Overall detection rate
    total_images = len(df)
    successful_detections = df['detection_success'].sum()
    detection_rate = successful_detections / total_images * 100
    
    print("\n===== FACE DETECTION RATE ANALYSIS =====\n")
    print(f"Overall Detection Rate: {detection_rate:.2f}% ({successful_detections}/{total_images})")
    
    # Detection rate by category
    category_stats = df.groupby('category').agg({
        'detection_success': ['count', 'sum', lambda x: x.sum() / len(x) * 100]
    })
    
    # Rename columns for better readability
    category_stats.columns = ['Total', 'Detected', 'Detection Rate (%)']
    
    print("\n----- Detection Rate by Category -----\n")
    print(tabulate(category_stats.sort_values(('Detection Rate (%)'), ascending=False), 
                  headers='keys', tablefmt='grid'))
    
    # Detection rate by image characteristics
    print("\n----- Detection Rate by Image Characteristics -----\n")
    
    # Extract image characteristics from filenames
    characteristics = []
    for idx, row in df.iterrows():
        image_name = row['image']
        
        # Skip base images
        if row['category'] == 'base':
            continue
        
        # Extract characteristics from filename
        if 'bright' in image_name:
            characteristics.append(('brightness', 'bright', row['detection_success']))
        elif 'dark' in image_name:
            characteristics.append(('brightness', 'dark', row['detection_success']))
        elif 'normal' in image_name:
            characteristics.append(('brightness', 'normal', row['detection_success']))
        
        if 'large' in image_name:
            characteristics.append(('size', 'large', row['detection_success']))
        elif 'small' in image_name:
            characteristics.append(('size', 'small', row['detection_success']))
        
        if 'high_quality' in image_name:
            characteristics.append(('quality', 'high', row['detection_success']))
        elif 'low_quality' in image_name:
            characteristics.append(('quality', 'low', row['detection_success']))
        
        if 'left15' in image_name:
            characteristics.append(('angle', 'left15', row['detection_success']))
        elif 'right15' in image_name:
            characteristics.append(('angle', 'right15', row['detection_success']))
        elif 'left30' in image_name:
            characteristics.append(('angle', 'left30', row['detection_success']))
        elif 'right30' in image_name:
            characteristics.append(('angle', 'right30', row['detection_success']))
        
        if 'sunglasses' in image_name:
            characteristics.append(('occlusion', 'sunglasses', row['detection_success']))
        elif 'mask' in image_name:
            characteristics.append(('occlusion', 'mask', row['detection_success']))
        elif 'hat' in image_name:
            characteristics.append(('occlusion', 'hat', row['detection_success']))
        elif 'shadow' in image_name:
            characteristics.append(('occlusion', 'shadow', row['detection_success']))
        
        if 'smile' in image_name:
            characteristics.append(('expression', 'smile', row['detection_success']))
        elif 'sad' in image_name:
            characteristics.append(('expression', 'sad', row['detection_success']))
        elif 'surprised' in image_name:
            characteristics.append(('expression', 'surprised', row['detection_success']))
        
        if 'white_bg' in image_name:
            characteristics.append(('background', 'white', row['detection_success']))
        elif 'black_bg' in image_name:
            characteristics.append(('background', 'black', row['detection_success']))
        elif 'blue_bg' in image_name:
            characteristics.append(('background', 'blue', row['detection_success']))
        elif 'green_bg' in image_name:
            characteristics.append(('background', 'green', row['detection_success']))
        elif 'gradient_bg' in image_name:
            characteristics.append(('background', 'gradient', row['detection_success']))
        elif 'noise_bg' in image_name:
            characteristics.append(('background', 'noise', row['detection_success']))
    
    # Convert to DataFrame
    char_df = pd.DataFrame(characteristics, columns=['factor', 'value', 'detected'])
    
    # Calculate detection rate by factor and value
    factor_stats = char_df.groupby(['factor', 'value']).agg({
        'detected': ['count', 'sum', lambda x: x.sum() / len(x) * 100]
    }).reset_index()
    
    # Rename columns
    factor_stats.columns = ['Factor', 'Value', 'Total', 'Detected', 'Detection Rate (%)']
    
    # Sort by factor and detection rate
    factor_stats = factor_stats.sort_values(['Factor', 'Detection Rate (%)'], ascending=[True, False])
    
    # Display results
    for factor in factor_stats['Factor'].unique():
        print(f"\n{factor.capitalize()} Factor:")
        factor_data = factor_stats[factor_stats['Factor'] == factor]
        print(tabulate(factor_data[['Value', 'Total', 'Detected', 'Detection Rate (%)']], 
                      headers='keys', tablefmt='grid'))
    
    return category_stats, factor_stats

def generate_visualizations(category_stats, factor_stats):
    """Generate visualizations of detection rates."""
    if category_stats is None or factor_stats is None:
        return
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Set style
    sns.set(style="whitegrid")
    
    # Plot detection rate by category
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=category_stats.index, y=category_stats['Detection Rate (%)'])
    plt.title('Face Detection Rate by Category')
    plt.xlabel('Category')
    plt.ylabel('Detection Rate (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Add value labels on bars
    for i, v in enumerate(category_stats['Detection Rate (%)']):
        ax.text(i, v + 1, f"{v:.1f}%", ha='center')
    
    # Save figure
    plt.savefig(os.path.join(OUTPUT_DIR, 'detection_rate_by_category.png'))
    print(f"Saved visualization to {os.path.join(OUTPUT_DIR, 'detection_rate_by_category.png')}")
    
    # Plot detection rate by factors
    for factor in factor_stats['Factor'].unique():
        plt.figure(figsize=(10, 6))
        factor_data = factor_stats[factor_stats['Factor'] == factor]
        ax = sns.barplot(x='Value', y='Detection Rate (%)', data=factor_data)
        plt.title(f'Face Detection Rate by {factor.capitalize()}')
        plt.xlabel(f'{factor.capitalize()} Value')
        plt.ylabel('Detection Rate (%)')
        plt.ylim(0, 105)  # Set y-axis limit to accommodate text labels
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Add value labels on bars
        for i, v in enumerate(factor_data['Detection Rate (%)']):
            ax.text(i, v + 1, f"{v:.1f}%", ha='center')
        
        # Save figure
        plt.savefig(os.path.join(OUTPUT_DIR, f'detection_rate_by_{factor}.png'))
        print(f"Saved visualization to {os.path.join(OUTPUT_DIR, f'detection_rate_by_{factor}.png')}")

def analyze_validation_rate(df):
    """Analyze validation rate by different factors."""
    if df is None or len(df) == 0:
        return
    
    # Overall validation rate
    total_images = len(df)
    valid_images = df['validation_valid'].sum()
    validation_rate = valid_images / total_images * 100
    
    print("\n===== FACE VALIDATION RATE ANALYSIS =====\n")
    print(f"Overall Validation Rate: {validation_rate:.2f}% ({valid_images}/{total_images})")
    
    # Validation rate by category
    category_stats = df.groupby('category').agg({
        'validation_valid': ['count', 'sum', lambda x: x.sum() / len(x) * 100]
    })
    
    # Rename columns for better readability
    category_stats.columns = ['Total', 'Valid', 'Validation Rate (%)']
    
    print("\n----- Validation Rate by Category -----\n")
    print(tabulate(category_stats.sort_values(('Validation Rate (%)'), ascending=False), 
                  headers='keys', tablefmt='grid'))
    
    # Analyze validation failure reasons
    print("\n----- Validation Failure Reasons -----\n")
    
    # Extract failure reasons from validation messages
    failure_reasons = []
    for idx, row in df.iterrows():
        if not row['validation_valid']:
            message = row['validation_message']
            
            if 'too dark' in message:
                reason = 'Too dark'
            elif 'too bright' in message:
                reason = 'Too bright'
            elif 'too small' in message:
                reason = 'Too small'
            elif 'Multiple faces' in message:
                reason = 'Multiple faces'
            elif 'No face' in message:
                reason = 'No face detected'
            else:
                reason = 'Other'
            
            failure_reasons.append((reason, row['category'], row['image']))
    
    # Convert to DataFrame
    reason_df = pd.DataFrame(failure_reasons, columns=['reason', 'category', 'image'])
    
    # Count by reason
    reason_counts = reason_df['reason'].value_counts().reset_index()
    reason_counts.columns = ['Reason', 'Count']
    reason_counts['Percentage'] = reason_counts['Count'] / len(failure_reasons) * 100
    
    print(tabulate(reason_counts, headers='keys', tablefmt='grid'))
    
    return reason_counts

def generate_recommendations(df, factor_stats):
    """Generate recommendations for improving detection rates."""
    if df is None or factor_stats is None:
        return
    
    print("\n===== RECOMMENDATIONS FOR IMPROVING DETECTION RATES =====\n")
    
    # Find problematic factors
    problematic_factors = []
    for factor in factor_stats['Factor'].unique():
        factor_data = factor_stats[factor_stats['Factor'] == factor]
        min_rate = factor_data['Detection Rate (%)'].min()
        min_value = factor_data.loc[factor_data['Detection Rate (%)'].idxmin(), 'Value']
        
        if min_rate < 90:  # Consider factors with detection rate < 90% as problematic
            problematic_factors.append((factor, min_value, min_rate))
    
    # Sort by detection rate (ascending)
    problematic_factors.sort(key=lambda x: x[2])
    
    if len(problematic_factors) == 0:
        print("No significant issues found. Detection rates are high across all factors.")
    else:
        print("The following factors have lower detection rates and should be addressed:")
        for factor, value, rate in problematic_factors:
            print(f"- {factor.capitalize()} = {value}: {rate:.2f}% detection rate")
        
        print("\nRecommendations:")
        for factor, value, rate in problematic_factors:
            if factor == 'occlusion' and value == 'sunglasses':
                print("1. Improve detection of faces with sunglasses:")
                print("   - Train the model with more examples of faces wearing sunglasses")
                print("   - Adjust detection parameters to be more sensitive to eye region features")
            elif factor == 'brightness' and (value == 'dark' or value == 'bright'):
                print(f"2. Improve detection in {value} images:")
                print("   - Implement image preprocessing to normalize brightness before detection")
                print("   - Add brightness adjustment step in the detection pipeline")
            elif factor == 'background' and (value == 'black' or value == 'white'):
                print(f"3. Improve detection with {value} backgrounds:")
                print("   - Enhance contrast detection in preprocessing step")
                print("   - Add background segmentation to isolate face from background")
    
    # Analyze validation failures
    invalid_images = df[~df['validation_valid']]
    validation_issues = invalid_images['validation_message'].value_counts()
    
    print("\nValidation Issues to Address:")
    for issue, count in validation_issues.items():
        print(f"- {issue}: {count} occurrences")
    
    print("\nRecommendations for Improving Validation Rate:")
    if 'too dark' in ' '.join(validation_issues.index):
        print("1. Implement brightness normalization in preprocessing")
    if 'too bright' in ' '.join(validation_issues.index):
        print("2. Add exposure correction for overly bright images")
    if 'too small' in ' '.join(validation_issues.index):
        print("3. Enhance detection of smaller faces or add upscaling step")
    if 'Multiple faces' in ' '.join(validation_issues.index):
        print("4. Improve face isolation in multi-face images")

def main():
    """Main function."""
    print("Starting face detection rate analysis...")
    
    # Load results
    df = load_results()
    if df is None:
        return
    
    # Analyze detection rate
    category_stats, factor_stats = analyze_detection_rate(df)
    
    # Generate visualizations
    generate_visualizations(category_stats, factor_stats)
    
    # Analyze validation rate
    reason_counts = analyze_validation_rate(df)
    
    # Generate recommendations
    generate_recommendations(df, factor_stats)
    
    print("\nFace detection rate analysis completed!")

if __name__ == "__main__":
    main()