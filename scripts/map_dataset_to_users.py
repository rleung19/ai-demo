#!/usr/bin/env python3
"""
Map dataset rows to ADMIN.USERS.ID
Supports multiple mapping strategies
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
    
    # Initialize Oracle client (simplified - reuse from test script logic)
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
        pass  # Try thin mode
    
    try:
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=connection_string
        )
        
        cursor = connection.cursor()
        
        # Get user IDs (prefer active users)
        if limit:
            query = f"""
                SELECT ID 
                FROM ADMIN.USERS 
                WHERE IS_ACTIVE = 1
                ORDER BY ID
                FETCH FIRST {limit} ROWS ONLY
            """
        else:
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

def map_dataset_to_users(dataset_file, output_file, strategy='multiple'):
    """
    Map dataset rows to USER_IDs
    
    Args:
        dataset_file: Path to dataset CSV
        output_file: Path to output CSV
        strategy: 'multiple' (10 rows per user) or 'sequential' (1:1 mapping)
    """
    
    print("=" * 60)
    print("Mapping Dataset to USER_IDs")
    print("=" * 60)
    
    # Load dataset
    print(f"\n📥 Loading dataset: {dataset_file}")
    df = pd.read_csv(dataset_file)
    print(f"   Dataset rows: {len(df):,}")
    
    # Get user IDs
    print(f"\n🔑 Fetching USER_IDs from ADMIN.USERS...")
    user_ids = get_user_ids()
    
    if not user_ids:
        print("❌ ERROR: Could not fetch user IDs")
        return False
    
    print(f"   Found {len(user_ids):,} active users")
    
    # Map dataset to users
    print(f"\n🔗 Mapping strategy: {strategy}")
    
    if strategy == 'multiple':
        # Map multiple rows per user (~10 rows per user)
        rows_per_user = len(df) // len(user_ids)
        print(f"   Mapping ~{rows_per_user} rows per user")
        
        mapped_user_ids = []
        for i in range(len(df)):
            user_idx = i % len(user_ids)
            mapped_user_ids.append(user_ids[user_idx])
        
        df['USER_ID'] = mapped_user_ids
        print(f"   ✅ Mapped {len(df):,} rows to {len(user_ids):,} users")
        print(f"   Each user appears ~{rows_per_user} times")
        
    elif strategy == 'sequential':
        # Map 1:1 (first N rows to N users)
        if len(df) > len(user_ids):
            print(f"   ⚠️  Dataset has more rows than users")
            print(f"   Using first {len(user_ids):,} rows")
            df = df.head(len(user_ids))
        
        df['USER_ID'] = user_ids[:len(df)]
        print(f"   ✅ Mapped {len(df):,} rows to {len(df):,} users (1:1)")
        print(f"   ⚠️  NOTE: Sequential may have bias - consider 'stratified' strategy")
        
    elif strategy == 'random':
        # Random sampling (maintains overall statistics)
        if len(df) > len(user_ids):
            print(f"   Randomly sampling {len(user_ids):,} rows from {len(df):,}")
            df = df.sample(n=len(user_ids), random_state=42).reset_index(drop=True)
        
        df['USER_ID'] = user_ids[:len(df)]
        churn_rate = df['Churned'].mean() * 100
        print(f"   ✅ Mapped {len(df):,} rows to {len(df):,} users (random)")
        print(f"   Churn rate: {churn_rate:.2f}%")
        
    elif strategy == 'stratified':
        # Stratified sampling (maintains exact churn rate)
        if len(df) > len(user_ids):
            print(f"   Stratified sampling {len(user_ids):,} rows from {len(df):,}")
            
            # Maintain churn rate
            churned = df[df['Churned']==1]
            not_churned = df[df['Churned']==0]
            full_churn_rate = len(churned) / len(df)
            
            n_churned = int(len(user_ids) * full_churn_rate)
            n_not_churned = len(user_ids) - n_churned
            
            print(f"   Target: {n_churned:,} churned + {n_not_churned:,} not churned")
            
            stratified = pd.concat([
                churned.sample(n=min(n_churned, len(churned)), random_state=42),
                not_churned.sample(n=min(n_not_churned, len(not_churned)), random_state=42)
            ]).sample(frac=1, random_state=42).reset_index(drop=True)
            
            df = stratified
        
        df['USER_ID'] = user_ids[:len(df)]
        churn_rate = df['Churned'].mean() * 100
        print(f"   ✅ Mapped {len(df):,} rows to {len(df):,} users (stratified)")
        print(f"   Churn rate: {churn_rate:.2f}% (maintains exact rate)")
        
    else:
        print(f"❌ ERROR: Unknown strategy: {strategy}")
        print(f"   Available: 'multiple', 'sequential', 'random', 'stratified'")
        return False
    
    # Reorder columns (USER_ID first, Churned last)
    cols = [col for col in df.columns if col not in ['USER_ID', 'Churned']]
    df = df[['USER_ID'] + cols + ['Churned']]
    
    # Save mapped dataset
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"\n💾 Saved mapped dataset to: {output_path}")
    print(f"   Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    # Summary
    print(f"\n" + "=" * 60)
    print("Mapping Summary")
    print("=" * 60)
    print(f"✅ Dataset rows: {len(df):,}")
    print(f"✅ Unique users: {df['USER_ID'].nunique():,}")
    print(f"✅ Strategy: {strategy}")
    
    if strategy == 'multiple':
        avg_rows_per_user = len(df) / df['USER_ID'].nunique()
        print(f"✅ Average rows per user: {avg_rows_per_user:.1f}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python map_dataset_to_users.py <dataset_file.csv> <output_file.csv> [strategy]")
        print("\nStrategies:")
        print("  multiple   - Map multiple rows per user (~10 rows per user, uses all 50k rows)")
        print("  sequential - Map 1:1 (first N rows to N users) - ⚠️  May have bias")
        print("  random     - Random sample 1:1 (maintains overall statistics) - ✅ Good")
        print("  stratified - Stratified sample 1:1 (maintains exact churn rate) - ✅ BEST")
        print("\nExample:")
        print("  python map_dataset_to_users.py data/processed/churn_dataset_cleaned.csv data/processed/churn_dataset_mapped.csv stratified")
        sys.exit(1)
    
    dataset_file = sys.argv[1]
    output_file = sys.argv[2]
    strategy = sys.argv[3] if len(sys.argv) > 3 else 'multiple'
    
    if not Path(dataset_file).exists():
        print(f"❌ ERROR: File not found: {dataset_file}")
        sys.exit(1)
    
    success = map_dataset_to_users(dataset_file, output_file, strategy)
    sys.exit(0 if success else 1)
