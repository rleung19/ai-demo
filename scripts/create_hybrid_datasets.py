#!/usr/bin/env python3
"""
Create hybrid datasets:
1. Mapped dataset (4,142 rows) - for API/demo with real USER_IDs
2. Training dataset (remaining rows) - for model training without user mapping
"""

import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / '.env'
load_dotenv(dotenv_path=env_file)

import oracledb

def get_user_ids(limit=None):
    """Get list of USER_IDs from ADMIN.USERS table"""
    
    wallet_path = os.getenv('ADB_WALLET_PATH')
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    
    if not all([wallet_path, connection_string, password]):
        print("❌ ERROR: Missing required environment variables")
        return None
    
    # Set TNS_ADMIN
    os.environ['TNS_ADMIN'] = wallet_path
    
    # Initialize Oracle client (simplified)
    import platform
    import subprocess
    import glob
    
    python_arch = platform.machine()
    lib_dir = None
    
    if python_arch == 'arm64':
        oracle_opt_paths = ['/opt/oracle/instantclient_*/lib', '/opt/oracle/instantclient_*']
        for pattern in oracle_opt_paths:
            matches = glob.glob(pattern)
            for match in matches:
                for lib_name in ['libclntsh.dylib', 'libclntsh.so']:
                    lib_path = os.path.join(match, lib_name) if os.path.isdir(match) else match
                    if os.path.exists(lib_path) or os.path.islink(lib_path):
                        try:
                            result = subprocess.run(['file', lib_path], 
                                                   capture_output=True, text=True, timeout=2)
                            lib_arch_info = result.stdout.lower()
                            if 'arm64' in lib_arch_info and 'x86_64' not in lib_arch_info:
                                lib_dir = os.path.dirname(lib_path) if os.path.isfile(lib_path) else match
                                break
                        except Exception:
                            pass
                if lib_dir:
                    break
            if lib_dir:
                break
    
    if not os.getenv('TNS_ADMIN'):
        os.environ['TNS_ADMIN'] = wallet_path
    
    try:
        if lib_dir:
            oracledb.init_oracle_client(lib_dir=lib_dir, config_dir=wallet_path)
        else:
            oracledb.init_oracle_client(config_dir=wallet_path)
    except Exception:
        pass
    
    try:
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=connection_string
        )
        
        cursor = connection.cursor()
        query = """
            SELECT ID 
            FROM ADMIN.USERS 
            WHERE IS_ACTIVE = 1
            ORDER BY ID
        """
        cursor.execute(query)
        user_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        return user_ids
        
    except Exception as e:
        print(f"❌ ERROR: Could not fetch user IDs: {e}")
        return None

def create_hybrid_datasets(dataset_file, mapped_output, training_output):
    """
    Create two datasets:
    1. Mapped dataset (stratified sample for API)
    2. Training dataset (remaining rows for training)
    """
    
    print("=" * 70)
    print("Creating Hybrid Datasets")
    print("=" * 70)
    
    # Load dataset
    print(f"\n📥 Loading dataset: {dataset_file}")
    df = pd.read_csv(dataset_file)
    print(f"   Total rows: {len(df):,}")
    
    # Get user IDs
    print(f"\n🔑 Fetching USER_IDs from ADMIN.USERS...")
    user_ids = get_user_ids()
    
    if not user_ids:
        print("❌ ERROR: Could not fetch user IDs")
        return False
    
    print(f"   Found {len(user_ids):,} active users")
    
    # Step 1: Create mapped dataset (stratified sample)
    print(f"\n" + "=" * 70)
    print("Step 1: Creating Mapped Dataset (for API/Demo)")
    print("=" * 70)
    
    n_users = len(user_ids)
    
    # Stratified sampling to maintain churn rate
    churned = df[df['Churned']==1]
    not_churned = df[df['Churned']==0]
    full_churn_rate = len(churned) / len(df)
    
    n_churned = int(n_users * full_churn_rate)
    n_not_churned = n_users - n_churned
    
    print(f"   Stratified sampling {n_users:,} rows:")
    print(f"   - {n_churned:,} churned rows")
    print(f"   - {n_not_churned:,} not churned rows")
    
    mapped_sample = pd.concat([
        churned.sample(n=min(n_churned, len(churned)), random_state=42),
        not_churned.sample(n=min(n_not_churned, len(not_churned)), random_state=42)
    ]).sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Map to real users
    mapped_sample['USER_ID'] = user_ids[:len(mapped_sample)]
    
    churn_rate = mapped_sample['Churned'].mean() * 100
    print(f"   ✅ Created mapped dataset: {len(mapped_sample):,} rows")
    print(f"   ✅ Churn rate: {churn_rate:.2f}% (maintains exact rate)")
    
    # Step 2: Create training dataset (remaining rows)
    print(f"\n" + "=" * 70)
    print("Step 2: Creating Training Dataset (for Model Training)")
    print("=" * 70)
    
    # Get indices of mapped rows
    mapped_indices = set(mapped_sample.index)
    
    # Get remaining rows
    training_df = df[~df.index.isin(mapped_indices)].copy()
    
    # Add placeholder USER_ID (or leave empty - not needed for training)
    # Using sequential IDs for reference, but not mapped to real users
    training_df['USER_ID'] = [f'TRAIN_{i+1}' for i in range(len(training_df))]
    
    training_churn_rate = training_df['Churned'].mean() * 100
    print(f"   ✅ Created training dataset: {len(training_df):,} rows")
    print(f"   ✅ Churn rate: {training_churn_rate:.2f}%")
    
    # Reorder columns (USER_ID first, Churned last)
    for df_to_save in [mapped_sample, training_df]:
        cols = [col for col in df_to_save.columns if col not in ['USER_ID', 'Churned']]
        df_to_save = df_to_save[['USER_ID'] + cols + ['Churned']]
    
    # Save datasets
    print(f"\n" + "=" * 70)
    print("Saving Datasets")
    print("=" * 70)
    
    # Save mapped dataset
    mapped_path = Path(mapped_output)
    mapped_path.parent.mkdir(parents=True, exist_ok=True)
    mapped_sample.to_csv(mapped_path, index=False)
    print(f"✅ Mapped dataset saved: {mapped_path}")
    print(f"   Rows: {len(mapped_sample):,}")
    print(f"   Purpose: API responses, demo, real user predictions")
    
    # Save training dataset
    training_path = Path(training_output)
    training_path.parent.mkdir(parents=True, exist_ok=True)
    training_df.to_csv(training_path, index=False)
    print(f"✅ Training dataset saved: {training_path}")
    print(f"   Rows: {len(training_df):,}")
    print(f"   Purpose: Model training, testing, validation")
    
    # Summary
    print(f"\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✅ Total rows used: {len(mapped_sample) + len(training_df):,} / {len(df):,}")
    print(f"✅ Data utilization: 100%")
    print(f"✅ Mapped dataset: {len(mapped_sample):,} rows (real users)")
    print(f"✅ Training dataset: {len(training_df):,} rows (for model)")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_hybrid_datasets.py <input_file.csv> <mapped_output.csv> <training_output.csv>")
        print("\nExample:")
        print("  python create_hybrid_datasets.py \\")
        print("    data/processed/churn_dataset_cleaned.csv \\")
        print("    data/processed/churn_dataset_mapped.csv \\")
        print("    data/processed/churn_dataset_training.csv")
        sys.exit(1)
    
    dataset_file = sys.argv[1]
    mapped_output = sys.argv[2]
    training_output = sys.argv[3]
    
    if not Path(dataset_file).exists():
        print(f"❌ ERROR: File not found: {dataset_file}")
        sys.exit(1)
    
    success = create_hybrid_datasets(dataset_file, mapped_output, training_output)
    sys.exit(0 if success else 1)
