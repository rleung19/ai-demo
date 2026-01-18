#!/usr/bin/env python3
"""
Examine dataset structure, quality, and features
"""

import pandas as pd
import sys
from pathlib import Path

def examine_dataset(file_path):
    """
    Examine a dataset file and provide detailed analysis
    """
    print("=" * 60)
    print("Dataset Examination Report")
    print("=" * 60)
    
    # Load dataset
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"❌ ERROR: Could not read file: {e}")
        return False
    
    print(f"\n📊 Basic Information")
    print(f"   File: {file_path}")
    print(f"   Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"   Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Column information
    print(f"\n📋 Columns ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df)) * 100
        unique_count = df[col].nunique()
        
        print(f"   {i:2d}. {col:30s} | {str(dtype):10s} | "
              f"Nulls: {null_count:5d} ({null_pct:5.1f}%) | "
              f"Unique: {unique_count:,}")
    
    # Check for churn label
    print(f"\n🎯 Churn Label Check")
    churn_keywords = ['churn', 'churned', 'is_churn', 'target', 'label']
    churn_cols = [col for col in df.columns 
                  if any(keyword in col.lower() for keyword in churn_keywords)]
    
    if churn_cols:
        print(f"   ✅ Found potential churn label(s): {churn_cols}")
        for col in churn_cols:
            print(f"\n   Analyzing '{col}':")
            value_counts = df[col].value_counts()
            print(f"      Value counts:")
            for val, count in value_counts.items():
                pct = (count / len(df)) * 100
                print(f"        {val}: {count:,} ({pct:.1f}%)")
            
            # Check if binary
            if len(value_counts) == 2:
                print(f"      ✅ Binary classification target")
                churn_rate = value_counts.get(1, value_counts.get('Yes', value_counts.get('Churned', 0)))
                if churn_rate > 0:
                    churn_pct = (churn_rate / len(df)) * 100
                    print(f"      Churn rate: {churn_pct:.1f}%")
    else:
        print(f"   ⚠️  No obvious churn label found")
        print(f"      Will need to derive churn (e.g., 90-day inactivity)")
    
    # Data quality
    print(f"\n🔍 Data Quality")
    total_cells = df.shape[0] * df.shape[1]
    null_cells = df.isnull().sum().sum()
    null_pct = (null_cells / total_cells) * 100
    
    print(f"   Total cells: {total_cells:,}")
    print(f"   Missing values: {null_cells:,} ({null_pct:.2f}%)")
    
    if null_pct > 5:
        print(f"   ⚠️  WARNING: High missing value rate (>5%)")
        print(f"      Columns with most missing values:")
        null_counts = df.isnull().sum().sort_values(ascending=False)
        for col, count in null_counts.head(5).items():
            if count > 0:
                pct = (count / len(df)) * 100
                print(f"        {col}: {count:,} ({pct:.1f}%)")
    else:
        print(f"   ✅ Good data quality (low missing values)")
    
    # Feature types
    print(f"\n📊 Feature Types")
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    print(f"   Numeric features: {len(numeric_cols)}")
    if numeric_cols:
        print(f"      {', '.join(numeric_cols[:10])}")
        if len(numeric_cols) > 10:
            print(f"      ... and {len(numeric_cols) - 10} more")
    
    print(f"   Categorical features: {len(categorical_cols)}")
    if categorical_cols:
        print(f"      {', '.join(categorical_cols[:10])}")
        if len(categorical_cols) > 10:
            print(f"      ... and {len(categorical_cols) - 10} more")
    
    # Sample data
    print(f"\n📄 Sample Data (first 5 rows):")
    print(df.head().to_string())
    
    # Summary statistics for numeric columns
    if numeric_cols:
        print(f"\n📈 Summary Statistics (numeric features):")
        print(df[numeric_cols].describe().to_string())
    
    # Check for ecommerce-relevant features
    print(f"\n🛒 Ecommerce Feature Check")
    ecommerce_keywords = [
        'order', 'purchase', 'spend', 'payment', 'device', 'login',
        'satisfaction', 'coupon', 'address', 'warehouse', 'city', 'tier'
    ]
    
    relevant_features = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ecommerce_keywords):
            relevant_features.append(col)
    
    if relevant_features:
        print(f"   ✅ Found {len(relevant_features)} ecommerce-relevant features:")
        for feat in relevant_features:
            print(f"      - {feat}")
    else:
        print(f"   ⚠️  No obvious ecommerce features found")
    
    print(f"\n" + "=" * 60)
    print("Examination Complete")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python examine_dataset.py <dataset_file.csv>")
        print("\nExample:")
        print("  python examine_dataset.py data/raw/ecommerce_customer_behavior.csv")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"❌ ERROR: File not found: {file_path}")
        sys.exit(1)
    
    examine_dataset(file_path)
