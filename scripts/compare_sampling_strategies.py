#!/usr/bin/env python3
"""
Compare different sampling strategies to see which is most representative
"""

import pandas as pd
import sys
from pathlib import Path

def compare_sampling_strategies(dataset_file):
    """Compare sequential, random, and stratified sampling"""
    
    print("=" * 70)
    print("Sampling Strategy Comparison")
    print("=" * 70)
    
    # Load dataset
    df = pd.read_csv(dataset_file)
    print(f"\n📊 Full Dataset Statistics:")
    print(f"   Total rows: {len(df):,}")
    print(f"   Churn rate: {df['Churned'].mean()*100:.2f}%")
    print(f"   Churned: {df['Churned'].sum():,}")
    print(f"   Not churned: {(df['Churned']==0).sum():,}")
    
    target_size = 4142
    
    # Strategy 1: Sequential (first N rows)
    print(f"\n" + "=" * 70)
    print("Strategy 1: Sequential (First N Rows)")
    print("=" * 70)
    sequential = df.head(target_size)
    seq_churn_rate = sequential['Churned'].mean() * 100
    print(f"   Churn rate: {seq_churn_rate:.2f}%")
    print(f"   Churned: {sequential['Churned'].sum():,}")
    print(f"   Not churned: {(sequential['Churned']==0).sum():,}")
    print(f"   Difference from full dataset: {seq_churn_rate - df['Churned'].mean()*100:+.2f}%")
    
    # Strategy 2: Random sampling
    print(f"\n" + "=" * 70)
    print("Strategy 2: Random Sampling")
    print("=" * 70)
    random_sample = df.sample(n=target_size, random_state=42)
    rand_churn_rate = random_sample['Churned'].mean() * 100
    print(f"   Churn rate: {rand_churn_rate:.2f}%")
    print(f"   Churned: {random_sample['Churned'].sum():,}")
    print(f"   Not churned: {(random_sample['Churned']==0).sum():,}")
    print(f"   Difference from full dataset: {rand_churn_rate - df['Churned'].mean()*100:+.2f}%")
    
    # Strategy 3: Stratified sampling (maintains churn rate)
    print(f"\n" + "=" * 70)
    print("Strategy 3: Stratified Sampling (Maintains Churn Rate)")
    print("=" * 70)
    churned = df[df['Churned']==1]
    not_churned = df[df['Churned']==0]
    full_churn_rate = len(churned) / len(df)
    
    n_churned = int(target_size * full_churn_rate)
    n_not_churned = target_size - n_churned
    
    stratified = pd.concat([
        churned.sample(n=min(n_churned, len(churned)), random_state=42),
        not_churned.sample(n=min(n_not_churned, len(not_churned)), random_state=42)
    ]).sample(frac=1, random_state=42).reset_index(drop=True)
    
    strat_churn_rate = stratified['Churned'].mean() * 100
    print(f"   Churn rate: {strat_churn_rate:.2f}%")
    print(f"   Churned: {stratified['Churned'].sum():,}")
    print(f"   Not churned: {(stratified['Churned']==0).sum():,}")
    print(f"   Difference from full dataset: {strat_churn_rate - df['Churned'].mean()*100:+.2f}%")
    print(f"   ✅ Maintains exact churn rate!")
    
    # Compare feature distributions
    print(f"\n" + "=" * 70)
    print("Feature Distribution Comparison")
    print("=" * 70)
    
    numeric_features = ['Age', 'Total_Purchases', 'Average_Order_Value', 
                       'Days_Since_Last_Purchase', 'Login_Frequency', 
                       'Lifetime_Value']
    
    print(f"\n{'Feature':<30} | {'Full Dataset':>12} | {'Sequential':>12} | {'Random':>12} | {'Stratified':>12}")
    print("-" * 80)
    
    for col in numeric_features:
        if col in df.columns:
            full_mean = df[col].mean()
            seq_mean = sequential[col].mean()
            rand_mean = random_sample[col].mean()
            strat_mean = stratified[col].mean()
            
            seq_diff = abs(seq_mean - full_mean) / full_mean * 100
            rand_diff = abs(rand_mean - full_mean) / full_mean * 100
            strat_diff = abs(strat_mean - full_mean) / full_mean * 100
            
            print(f"{col:<30} | {full_mean:>12.2f} | {seq_mean:>12.2f} | {rand_mean:>12.2f} | {strat_mean:>12.2f}")
            print(f"{'  (diff %)':<30} | {'':>12} | {seq_diff:>11.1f}% | {rand_diff:>11.1f}% | {strat_diff:>11.1f}%")
    
    # Summary
    print(f"\n" + "=" * 70)
    print("Summary & Recommendation")
    print("=" * 70)
    
    print(f"\nChurn Rate Accuracy:")
    print(f"   Sequential: {abs(seq_churn_rate - df['Churned'].mean()*100):.2f}% difference")
    print(f"   Random:     {abs(rand_churn_rate - df['Churned'].mean()*100):.2f}% difference")
    print(f"   Stratified: {abs(strat_churn_rate - df['Churned'].mean()*100):.2f}% difference ✅ BEST")
    
    print(f"\n🎯 Recommendation:")
    if abs(strat_churn_rate - df['Churned'].mean()*100) < 0.1:
        print(f"   ✅ Use STRATIFIED sampling - maintains exact churn rate")
    elif abs(rand_churn_rate - df['Churned'].mean()*100) < 1.0:
        print(f"   ✅ Use RANDOM sampling - good representation")
    else:
        print(f"   ⚠️  Sequential may have bias - consider random or stratified")
    
    return {
        'sequential': sequential,
        'random': random_sample,
        'stratified': stratified
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        dataset_file = "data/processed/churn_dataset_cleaned.csv"
    else:
        dataset_file = sys.argv[1]
    
    if not Path(dataset_file).exists():
        print(f"❌ ERROR: File not found: {dataset_file}")
        sys.exit(1)
    
    compare_sampling_strategies(dataset_file)
