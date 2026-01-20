#!/usr/bin/env python3
"""
Download Kaggle dataset using Kaggle API
Requires: pip install kaggle
Setup: Place kaggle.json in ~/.kaggle/ (or set KAGGLE_USERNAME and KAGGLE_KEY env vars)
"""

import os
import sys
from pathlib import Path

def download_dataset(dataset_name, output_dir="data/raw"):
    """
    Download a Kaggle dataset
    
    Args:
        dataset_name: Kaggle dataset name (e.g., "dhairyajeetsingh/ecommerce-customer-behavior-dataset")
        output_dir: Directory to save downloaded files
    """
    try:
        import kaggle
    except ImportError:
        print("❌ ERROR: kaggle package not installed")
        print("   Install with: pip install kaggle")
        print("   Then set up Kaggle API credentials:")
        print("   1. Go to https://www.kaggle.com/settings")
        print("   2. Create API token (downloads kaggle.json)")
        print("   3. Place kaggle.json in ~/.kaggle/")
        return False
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Downloading dataset: {dataset_name}")
    print(f"   Saving to: {output_path.absolute()}")
    
    try:
        kaggle.api.dataset_download_files(
            dataset_name,
            path=str(output_path),
            unzip=True
        )
        print(f"✅ Dataset downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to download dataset: {e}")
        print("\nTroubleshooting:")
        print("1. Verify dataset name is correct")
        print("2. Check Kaggle API credentials are set up")
        print("3. Ensure you have access to the dataset")
        return False

if __name__ == "__main__":
    # Try to find the dhairyajeetsingh dataset
    # Common variations of the dataset name
    possible_names = [
        "dhairyajeetsingh/ecommerce-customer-behavior-dataset",
        "dhairyajeetsingh/ecommerce-customer-churn-dataset",
        "dhairyajeetsingh/ecommerce-customer-behavior",
    ]
    
    print("=" * 60)
    print("Kaggle Dataset Downloader")
    print("=" * 60)
    print("\nNote: This script requires Kaggle API setup")
    print("If you haven't set it up, you can:")
    print("1. Download manually from Kaggle website")
    print("2. Or set up Kaggle API (see instructions above)")
    print()
    
    # Try each possible name
    success = False
    for dataset_name in possible_names:
        print(f"\nTrying: {dataset_name}")
        if download_dataset(dataset_name):
            success = True
            break
    
    if not success:
        print("\n⚠️  Could not download automatically")
        print("   Please download manually from Kaggle:")
        print("   https://www.kaggle.com/datasets")
        print("   Search for: 'dhairyajeetsingh ecommerce customer behavior'")
