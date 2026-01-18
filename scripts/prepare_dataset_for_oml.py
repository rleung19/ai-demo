#!/usr/bin/env python3
"""
Prepare dataset for loading into OML schema
- Handle missing values
- Fix data anomalies
- Map to USER_ID
- Export for database loading
"""

import pandas as pd
import sys
from pathlib import Path

def prepare_dataset(input_file, output_file=None, user_id_mapping=None):
    """
    Prepare dataset for OML schema loading
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file (optional)
        user_id_mapping: Dictionary mapping dataset index to USER_ID (optional)
    """
    print("=" * 60)
    print("Dataset Preparation for OML Schema")
    print("=" * 60)
    
    # Load dataset
    print(f"\n📥 Loading dataset: {input_file}")
    df = pd.read_csv(input_file)
    print(f"   Original shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    # Step 1: Handle missing values
    print(f"\n🔧 Step 1: Handling Missing Values")
    original_missing = df.isnull().sum().sum()
    print(f"   Original missing values: {original_missing:,}")
    
    # For numeric columns: use median imputation
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    numeric_cols = [col for col in numeric_cols if col != 'Churned']  # Don't impute target
    
    for col in numeric_cols:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            median_val = df[col].median()
            df.loc[:, col] = df[col].fillna(median_val)
            print(f"   ✓ Filled {missing_count:,} missing values in '{col}' with median: {median_val:.2f}")
    
    # For categorical columns: use mode imputation
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown'
            df.loc[:, col] = df[col].fillna(mode_val)
            print(f"   ✓ Filled {missing_count:,} missing values in '{col}' with mode: {mode_val}")
    
    remaining_missing = df.isnull().sum().sum()
    print(f"   Remaining missing values: {remaining_missing:,}")
    
    # Step 2: Fix data anomalies
    print(f"\n🔧 Step 2: Fixing Data Anomalies")
    
    # Fix negative Total_Purchases
    if 'Total_Purchases' in df.columns:
        negative_count = (df['Total_Purchases'] < 0).sum()
        if negative_count > 0:
            df.loc[df['Total_Purchases'] < 0, 'Total_Purchases'] = 0
            print(f"   ✓ Fixed {negative_count:,} negative Total_Purchases (set to 0)")
    
    # Cap Age outliers (reasonable range: 18-100)
    if 'Age' in df.columns:
        outliers = ((df['Age'] < 18) | (df['Age'] > 100)).sum()
        if outliers > 0:
            df.loc[df['Age'] < 18, 'Age'] = 18
            df.loc[df['Age'] > 100, 'Age'] = 100
            print(f"   ✓ Capped {outliers:,} Age outliers (set to 18-100 range)")
    
    # Cap extreme Average_Order_Value (e.g., > 5000)
    if 'Average_Order_Value' in df.columns:
        extreme_count = (df['Average_Order_Value'] > 5000).sum()
        if extreme_count > 0:
            p99 = df['Average_Order_Value'].quantile(0.99)
            df.loc[df['Average_Order_Value'] > 5000, 'Average_Order_Value'] = p99
            print(f"   ✓ Capped {extreme_count:,} extreme Average_Order_Value values (99th percentile: {p99:.2f})")
    
    # Step 3: Add USER_ID mapping
    print(f"\n🔧 Step 3: Adding USER_ID Mapping")
    
    if user_id_mapping:
        # Use provided mapping
        df['USER_ID'] = df.index.map(user_id_mapping)
        print(f"   ✓ Mapped to USER_ID using provided mapping")
    else:
        # Create placeholder USER_ID (will be mapped later)
        df['USER_ID'] = df.index + 1  # 1-indexed
        print(f"   ✓ Created placeholder USER_ID (1 to {len(df)})")
        print(f"   ⚠️  NOTE: Will need to map to actual ADMIN.USERS.ID later")
    
    # Step 4: Ensure Churned column is properly named
    if 'Churned' in df.columns:
        print(f"   ✓ Churn label found: 'Churned'")
        churn_rate = df['Churned'].mean() * 100
        print(f"      Churn rate: {churn_rate:.1f}%")
    
    # Step 5: Reorder columns (USER_ID first, Churned last)
    cols = [col for col in df.columns if col not in ['USER_ID', 'Churned']]
    df = df[['USER_ID'] + cols + ['Churned']]
    
    # Step 6: Save prepared dataset
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"\n💾 Saved prepared dataset to: {output_path}")
        print(f"   Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    else:
        print(f"\n📊 Prepared dataset (not saved)")
        print(f"   Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    # Summary
    print(f"\n" + "=" * 60)
    print("Preparation Summary")
    print("=" * 60)
    print(f"✅ Missing values handled")
    print(f"✅ Data anomalies fixed")
    print(f"✅ USER_ID mapping added")
    print(f"✅ Dataset ready for OML schema loading")
    
    return df

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prepare_dataset_for_oml.py <input_file.csv> [output_file.csv]")
        print("\nExample:")
        print("  python prepare_dataset_for_oml.py data/raw/ecommerce_customer_churn_dataset.csv data/processed/churn_dataset_cleaned.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(input_file).exists():
        print(f"❌ ERROR: File not found: {input_file}")
        sys.exit(1)
    
    prepare_dataset(input_file, output_file)
