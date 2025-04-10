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
# PART B: Class-Level Analysis (All Metrics)
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
    
    # Generate boxplot with clean data
    plt.figure(figsize=(8, 5))
    try:
        sns.boxplot(x='Tag', y=metric, data=clean_data, notch=True)
        plt.title(f'{metric} by Version')
        plt.savefig(f'outputs/{metric}_boxplot.png', bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Could not create boxplot for {metric}: {str(e)}")