import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Create outputs directory
os.makedirs("outputs", exist_ok=True)

# Read and combine all CSV files
files = {
    "r5.11.4": "r5.11.4-filtered.csv",
    "r5.12.0": "r5.12.0-filtered.csv",
    "r5.12.1": "r5.12.1-filtered.csv"
}

all_data = pd.DataFrame()
for tag, file in files.items():
    df = pd.read_csv(file)
    df['Tag'] = tag
    # Add a unique identifier to prevent duplicates
    df['unique_id'] = range(len(df))
    all_data = pd.concat([all_data, df])

# Remove any exact duplicates that might exist
all_data = all_data.drop_duplicates()

# Filter for classes and methods separately
class_data = all_data[all_data['Kind'].isin(['Private Class', 'Public Class'])].copy()
method_data = all_data[all_data['Kind'].isin(['Private Method', 'Public Method', 'Protected Method'])].copy()

# =================================================================
# PART A: Quality Characteristics Mapping (All Metrics)
# =================================================================
quality_mapping = {
    'SumCyclomatic': "Total cyclomatic complexity (Sum CC)",
    'AvgEssential': "Average essential complexity (Avg. EC)",
    'MaxInheritanceTree': "Depth of inheritance tree (DIT)",
    'PercentLackOfCohesion': "Lack of cohesion (LCOM)",
    'CountClassDerived': "Number of children (NOC)",
    'CountClassCoupled': "Coupling between objects (CBO)",
    'CountDeclMethod': "Weighted methods per class (WMC)",
    'CountLineCode': "Source lines of code (SLOC)"
}

print("=== PART A: Quality Characteristics ===")
for metric, desc in quality_mapping.items():
    print(f"{metric:<20}: {desc}")

# =================================================================
# PART B: Class-Level Analysis (All Metrics) - IMPROVED VERSION
# =================================================================
class_metrics = [
    'SumCyclomatic',
    'MaxInheritanceTree',
    'PercentLackOfCohesion',
    'CountClassDerived',
    'CountClassCoupled',
    'CountDeclMethod',
    'CountLineCode'
]

# Set consistent figure size for all plots
plt.figure(figsize=(10, 6))

print("\n=== PART B: Class-Level Analysis ===")
for metric in class_metrics:
    if metric not in class_data.columns:
        print(f"\nSkipping {metric} - not found in data")
        continue

    # Clean data - drop NaN values for this metric
    clean_data = class_data.dropna(subset=[metric])
    
    # B.i: Statistical Summary
    stats = clean_data.groupby('Tag')[metric].describe()
    print(f"\n--- {metric} ---")
    print(stats[['50%', '25%', '75%', 'min', 'max']].rename(columns={'50%': 'median'}))
    
    # B.ii: Quality Trend
    medians = clean_data.groupby('Tag')[metric].median()
    trend = "increasing" if medians.is_monotonic_increasing else \
            "decreasing" if medians.is_monotonic_decreasing else "stable"
    print(f"Trend: {trend}")
    
    # B.iii: Guideline Comparison (for specific metrics)
    if metric == 'MaxInheritanceTree':
        print("\nDIT Assessment:")
        for tag, value in medians.items():
            assessment = "Too high (>6)" if value > 6 else \
                        "Too low (<2)" if value < 2 else "Optimal (2-6)"
            print(f"{tag}: {value:.1f} → {assessment}")
    
    elif metric == 'PercentLackOfCohesion':
        print("\nLCOM Assessment:")
        for tag, value in medians.items():
            assessment = "Poor (>80%)" if value > 80 else \
                        "Moderate (50-80%)" if value > 50 else "Good (<50%)"
            print(f"{tag}: {value:.1f}% → {assessment}")
    
    elif metric == 'SumCyclomatic':
        print("\nCyclomatic Complexity Assessment:")
        for tag, value in medians.items():
            assessment = "High (>50)" if value > 50 else \
                        "Moderate (20-50)" if value > 20 else "Low (<20)"
            print(f"{tag}: {value:.1f} → {assessment}")
    
    # Generate IMPROVED boxplot with clean data
    plt.figure(figsize=(10, 6))
    try:

         # Determine which metrics should have notches
        if metric in ['CountClassDerived', 'MaxInheritanceTree', 'CountClassCoupled']:
            use_notch = False  # Disable notches for these discrete metrics
        else:
            use_notch = True   # Enable notches for continuous metrics

        # Create boxplot with notches and proper formatting
        sns.boxplot(
            x='Tag', 
            y=metric, 
            data=clean_data, 
            notch=True,  # Add notches for median confidence intervals
            showfliers=True,  # Show outliers
            width=0.5,  # Control box width
            palette="Set2"  # Use a pleasant color palette
        )
        
        # Calculate and show the 1.5*IQR threshold line
        q1 = clean_data[metric].quantile(0.25)
        q3 = clean_data[metric].quantile(0.75)
        iqr = q3 - q1
        upper_threshold = q3 + 1.5 * iqr
        lower_threshold = q1 - 1.5 * iqr
        
        # Add proper labels and title
        plt.title(f'Distribution of {quality_mapping.get(metric, metric)} by Version', pad=20)
        plt.xlabel('Software Version', labelpad=10)
        plt.ylabel(quality_mapping.get(metric, metric), labelpad=10)
        
        # Adjust y-axis limits to show outliers but not too much empty space
         # Special y-axis handling for discrete metrics
        if metric in ['CountClassDerived', 'MaxInheritanceTree']:
            max_val = int(clean_data[metric].max())
            plt.yticks(range(0, max_val + 1))
            plt.ylim(-0.5, max_val + 0.5)
        else:
            y_min = max(clean_data[metric].min(), lower_threshold - iqr)
            y_max = min(clean_data[metric].max(), upper_threshold + iqr)
            plt.ylim(y_min, y_max)
        
        # Add grid for better readability
        plt.grid(axis='y', alpha=0.3)
        # Save with high DPI and tight layout
        plt.tight_layout()
        plt.savefig(f'outputs/{metric}_boxplot.png', dpi=300, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Could not create boxplot for {metric}: {str(e)}")