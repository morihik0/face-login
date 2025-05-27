"""
Script to analyze false authentication rates from test results.

This script analyzes the face authentication test results to measure false authentication rates
under different conditions and identify factors that contribute to false authentications.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

# Define paths
RESULTS_DIR = 'tests/results/authentication'
RESULTS_FILE = os.path.join(RESULTS_DIR, 'authentication_test_results.csv')
OUTPUT_DIR = os.path.join(RESULTS_DIR, 'false_rate_analysis')

def load_results():
    """Load authentication test results from CSV file."""
    if not os.path.exists(RESULTS_FILE):
        print(f"Error: Results file not found at {RESULTS_FILE}")
        return None
    
    try:
        df = pd.read_csv(RESULTS_FILE)
        print(f"Loaded {len(df)} authentication test results")
        return df
    except Exception as e:
        print(f"Error loading results: {e}")
        return None

def calculate_error_rates(df):
    """Calculate false positive and false negative rates by threshold."""
    if df is None or len(df) == 0:
        return None
    
    # Group by threshold
    threshold_groups = df.groupby('threshold')
    
    error_rates = []
    
    for threshold, group in threshold_groups:
        total = len(group)
        positives = group['expected_user_id'].notna().sum()  # Number of images with expected users
        negatives = total - positives  # Number of images without expected users
        
        # Calculate metrics
        false_positives = group['false_positive'].sum()
        false_negatives = group['false_negative'].sum()
        true_positives = group['true_positive'].sum()
        true_negatives = group['true_negative'].sum()
        
        # Calculate rates
        fpr = false_positives / negatives if negatives > 0 else 0  # False Positive Rate
        fnr = false_negatives / positives if positives > 0 else 0  # False Negative Rate
        
        error_rates.append({
            'threshold': threshold,
            'total': total,
            'positives': positives,
            'negatives': negatives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'true_positives': true_positives,
            'true_negatives': true_negatives,
            'false_positive_rate': fpr,
            'false_negative_rate': fnr,
            'error_rate': (false_positives + false_negatives) / total if total > 0 else 0
        })
    
    return pd.DataFrame(error_rates)

def analyze_error_factors(df):
    """Analyze factors contributing to false authentications."""
    if df is None or len(df) == 0:
        return None
    
    # Filter for the default threshold (0.6)
    df_default = df[df['threshold'] == 0.6]
    
    # Analyze false negatives by category
    false_negatives = df_default[df_default['false_negative']]
    fn_by_category = false_negatives.groupby('category').size().reset_index(name='count')
    fn_by_category['percentage'] = fn_by_category['count'] / len(false_negatives) * 100
    
    # Analyze false positives by category
    false_positives = df_default[df_default['false_positive']]
    fp_by_category = false_positives.groupby('category').size().reset_index(name='count')
    fp_by_category['percentage'] = fp_by_category['count'] / len(false_positives) * 100 if len(false_positives) > 0 else 0
    
    # Analyze error rates by image characteristics
    error_by_image = []
    
    for idx, row in df_default.iterrows():
        image_name = row['image_name']
        
        # Skip if no error
        if not (row['false_negative'] or row['false_positive']):
            continue
        
        # Extract characteristics from filename
        characteristics = []
        
        if 'bright' in image_name:
            characteristics.append('bright')
        elif 'dark' in image_name:
            characteristics.append('dark')
        elif 'normal' in image_name:
            characteristics.append('normal')
        
        if 'large' in image_name:
            characteristics.append('large')
        elif 'small' in image_name:
            characteristics.append('small')
        
        if 'high_quality' in image_name:
            characteristics.append('high_quality')
        elif 'low_quality' in image_name:
            characteristics.append('low_quality')
        
        if 'left15' in image_name or 'right15' in image_name:
            characteristics.append('angle_15')
        elif 'left30' in image_name or 'right30' in image_name:
            characteristics.append('angle_30')
        
        if 'sunglasses' in image_name:
            characteristics.append('sunglasses')
        elif 'mask' in image_name:
            characteristics.append('mask')
        elif 'hat' in image_name:
            characteristics.append('hat')
        elif 'shadow' in image_name:
            characteristics.append('shadow')
        
        if 'smile' in image_name:
            characteristics.append('smile')
        elif 'sad' in image_name:
            characteristics.append('sad')
        elif 'surprised' in image_name:
            characteristics.append('surprised')
        
        if 'white_bg' in image_name:
            characteristics.append('white_bg')
        elif 'black_bg' in image_name:
            characteristics.append('black_bg')
        elif 'blue_bg' in image_name:
            characteristics.append('blue_bg')
        elif 'green_bg' in image_name:
            characteristics.append('green_bg')
        elif 'gradient_bg' in image_name:
            characteristics.append('gradient_bg')
        elif 'noise_bg' in image_name:
            characteristics.append('noise_bg')
        
        for characteristic in characteristics:
            error_by_image.append({
                'characteristic': characteristic,
                'false_negative': row['false_negative'],
                'false_positive': row['false_positive'],
                'error_type': 'false_negative' if row['false_negative'] else 'false_positive'
            })
    
    # Convert to DataFrame
    error_by_characteristic = pd.DataFrame(error_by_image)
    
    # Count errors by characteristic
    if len(error_by_characteristic) > 0:
        char_counts = error_by_characteristic.groupby(['characteristic', 'error_type']).size().reset_index(name='count')
    else:
        char_counts = pd.DataFrame(columns=['characteristic', 'error_type', 'count'])
    
    return {
        'fn_by_category': fn_by_category,
        'fp_by_category': fp_by_category,
        'error_by_characteristic': char_counts
    }

def generate_report(error_rates, error_factors):
    """Generate a report on false authentication rates."""
    if error_rates is None or error_factors is None:
        return
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("\n===== FALSE AUTHENTICATION RATE ANALYSIS =====\n")
    
    # Print error rates by threshold
    print("----- Error Rates by Threshold -----\n")
    rate_table = error_rates[['threshold', 'false_positive_rate', 'false_negative_rate', 'error_rate']]
    rate_table = rate_table.sort_values('threshold')
    
    # Convert rates to percentages for display
    display_table = rate_table.copy()
    display_table[['false_positive_rate', 'false_negative_rate', 'error_rate']] *= 100
    
    print(tabulate(display_table, headers='keys', tablefmt='grid', floatfmt='.2f'))
    
    # Find the threshold with the lowest error rate
    min_error_idx = error_rates['error_rate'].idxmin()
    best_threshold = error_rates.loc[min_error_idx, 'threshold']
    min_error_rate = error_rates.loc[min_error_idx, 'error_rate'] * 100
    
    print(f"\nLowest error rate: {min_error_rate:.2f}% at threshold {best_threshold}")
    
    # Print false negative analysis by category
    fn_by_category = error_factors['fn_by_category']
    if len(fn_by_category) > 0:
        print("\n----- False Negative Rate by Category -----\n")
        fn_table = fn_by_category.sort_values('count', ascending=False)
        print(tabulate(fn_table, headers='keys', tablefmt='grid', floatfmt='.2f'))
    
    # Print false positive analysis by category
    fp_by_category = error_factors['fp_by_category']
    if len(fp_by_category) > 0:
        print("\n----- False Positive Rate by Category -----\n")
        fp_table = fp_by_category.sort_values('count', ascending=False)
        print(tabulate(fp_table, headers='keys', tablefmt='grid', floatfmt='.2f'))
    
    # Print error analysis by characteristic
    error_by_char = error_factors['error_by_characteristic']
    if len(error_by_char) > 0:
        print("\n----- Errors by Image Characteristic -----\n")
        char_table = error_by_char.sort_values(['error_type', 'count'], ascending=[True, False])
        print(tabulate(char_table, headers='keys', tablefmt='grid'))
    
    # Generate visualizations
    
    # 1. Error rates vs threshold
    plt.figure(figsize=(10, 6))
    plt.plot(rate_table['threshold'], rate_table['false_positive_rate'] * 100, 'o-', label='False Positive Rate')
    plt.plot(rate_table['threshold'], rate_table['false_negative_rate'] * 100, 'o-', label='False Negative Rate')
    plt.plot(rate_table['threshold'], rate_table['error_rate'] * 100, 'o-', label='Overall Error Rate')
    
    plt.axvline(x=best_threshold, color='r', linestyle='--', label=f'Best Threshold ({best_threshold})')
    
    plt.xlabel('Threshold')
    plt.ylabel('Error Rate (%)')
    plt.title('Authentication Error Rates vs Threshold')
    plt.legend()
    plt.grid(True)
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'error_rates_vs_threshold.png'))
    print(f"\nSaved error rates plot to {os.path.join(OUTPUT_DIR, 'error_rates_vs_threshold.png')}")
    
    # 2. False negative by category
    if len(fn_by_category) > 0:
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x='category', y='count', data=fn_by_category.sort_values('count', ascending=False))
        plt.title('False Negatives by Category')
        plt.xlabel('Category')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Add value labels on bars
        for i, v in enumerate(fn_by_category.sort_values('count', ascending=False)['count']):
            ax.text(i, v + 0.1, str(int(v)), ha='center')
        
        plt.savefig(os.path.join(OUTPUT_DIR, 'false_negatives_by_category.png'))
        print(f"Saved false negatives plot to {os.path.join(OUTPUT_DIR, 'false_negatives_by_category.png')}")
    
    # 3. Errors by characteristic
    if len(error_by_char) > 0:
        # Pivot the data for plotting
        pivot_data = error_by_char.pivot_table(index='characteristic', columns='error_type', values='count', fill_value=0)
        
        plt.figure(figsize=(12, 8))
        pivot_data.plot(kind='bar', figsize=(12, 8))
        plt.title('Errors by Image Characteristic')
        plt.xlabel('Characteristic')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend(title='Error Type')
        plt.tight_layout()
        
        plt.savefig(os.path.join(OUTPUT_DIR, 'errors_by_characteristic.png'))
        print(f"Saved errors by characteristic plot to {os.path.join(OUTPUT_DIR, 'errors_by_characteristic.png')}")
    
    # Save results to CSV
    error_rates.to_csv(os.path.join(OUTPUT_DIR, 'error_rates_by_threshold.csv'), index=False)
    print(f"\nSaved error rates to {os.path.join(OUTPUT_DIR, 'error_rates_by_threshold.csv')}")
    
    if len(fn_by_category) > 0:
        fn_by_category.to_csv(os.path.join(OUTPUT_DIR, 'false_negatives_by_category.csv'), index=False)
        print(f"Saved false negatives by category to {os.path.join(OUTPUT_DIR, 'false_negatives_by_category.csv')}")
    
    if len(fp_by_category) > 0:
        fp_by_category.to_csv(os.path.join(OUTPUT_DIR, 'false_positives_by_category.csv'), index=False)
        print(f"Saved false positives by category to {os.path.join(OUTPUT_DIR, 'false_positives_by_category.csv')}")
    
    if len(error_by_char) > 0:
        error_by_char.to_csv(os.path.join(OUTPUT_DIR, 'errors_by_characteristic.csv'), index=False)
        print(f"Saved errors by characteristic to {os.path.join(OUTPUT_DIR, 'errors_by_characteristic.csv')}")
    
    # Generate recommendations
    print("\n===== RECOMMENDATIONS FOR REDUCING FALSE AUTHENTICATION RATES =====\n")
    
    # Analyze false negatives
    if len(fn_by_category) > 0:
        print("Recommendations for reducing false negatives (authentication failures for valid users):")
        
        # Get top categories with false negatives
        top_fn_categories = fn_by_category.sort_values('count', ascending=False).head(3)
        
        for _, row in top_fn_categories.iterrows():
            category = row['category']
            count = row['count']
            
            if category == 'backgrounds':
                print("1. Improve authentication with different backgrounds:")
                print("   - Implement background segmentation to isolate face from background")
                print("   - Train the model with more examples of faces against various backgrounds")
            elif category == 'brightness':
                print("2. Improve authentication with different lighting conditions:")
                print("   - Add preprocessing step to normalize brightness before authentication")
                print("   - Implement adaptive thresholding based on image brightness")
            elif category == 'occlusions':
                print("3. Improve authentication with facial occlusions:")
                print("   - Train the model to focus on visible facial features")
                print("   - Implement partial face matching for occluded faces")
    
    # Analyze false positives
    if len(fp_by_category) > 0 and fp_by_category['count'].sum() > 0:
        print("\nRecommendations for reducing false positives (incorrect authentications):")
        
        # Get top categories with false positives
        top_fp_categories = fp_by_category.sort_values('count', ascending=False).head(3)
        
        for _, row in top_fp_categories.iterrows():
            category = row['category']
            count = row['count']
            
            if category == 'expressions':
                print("1. Improve discrimination with different expressions:")
                print("   - Train the model with more examples of facial expressions")
                print("   - Increase the authentication threshold for unusual expressions")
            elif category == 'angles':
                print("2. Improve discrimination with different face angles:")
                print("   - Train the model with more examples of rotated faces")
                print("   - Implement 3D face modeling for better angle handling")
    
    # General recommendations based on error rates
    print("\nGeneral recommendations:")
    
    # Find the optimal threshold
    if len(error_rates) > 0:
        print(f"1. Set the authentication threshold to {best_threshold} for optimal balance between false positives and negatives")
    
    print("2. Implement multi-factor authentication for high-security scenarios")
    print("3. Use multiple face images per user to improve recognition across different conditions")
    print("4. Implement adaptive thresholding based on image quality and lighting conditions")

def main():
    """Main function."""
    print("Starting false authentication rate analysis...")
    
    # Load results
    df = load_results()
    if df is None:
        return
    
    # Calculate error rates
    error_rates = calculate_error_rates(df)
    
    # Analyze error factors
    error_factors = analyze_error_factors(df)
    
    # Generate report
    generate_report(error_rates, error_factors)
    
    print("\nFalse authentication rate analysis completed!")

if __name__ == "__main__":
    main()