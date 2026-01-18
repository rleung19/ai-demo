#!/usr/bin/env python3
"""
Data Ingestion Script for Churn Prediction Model
Loads CSV files into Oracle ADB OML schema tables

Usage:
    python scripts/ingest_churn_data.py

Prerequisites:
    - Oracle Instant Client installed
    - oracledb package installed (pip install oracledb)
    - ADB wallet configured
    - Environment variables set (.env file)
    - Tables created (run sql/create_churn_tables.sql first)
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Find project root (parent of scripts directory)
script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / '.env'

# Load environment variables
try:
    from dotenv import load_dotenv
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        print(f"✓ Loaded .env file from: {env_file}")
    else:
        print(f"⚠️  WARNING: .env file not found at {env_file}")
        load_dotenv()
except ImportError:
    print("⚠️  WARNING: python-dotenv not installed.")
    print("   Install with: pip install python-dotenv")
    print("   Using system environment variables only.")

def initialize_oracle_client():
    """Initialize Oracle client with wallet support"""
    try:
        import oracledb
    except ImportError:
        print("❌ ERROR: oracledb not installed")
        print("   Install with: pip install oracledb")
        sys.exit(1)
    
    wallet_path = os.getenv('ADB_WALLET_PATH')
    if not wallet_path:
        print("❌ ERROR: ADB_WALLET_PATH not set in environment")
        print(f"   Check .env file at: {env_file}")
        sys.exit(1)
    
    if not os.path.exists(wallet_path):
        print(f"❌ ERROR: Wallet path does not exist: {wallet_path}")
        sys.exit(1)
    
    # Set TNS_ADMIN if not already set
    if not os.getenv('TNS_ADMIN'):
        os.environ['TNS_ADMIN'] = wallet_path
    
    # Try to initialize Oracle client (thick mode)
    try:
        # Try common ARM64 paths first (for Apple Silicon)
        import glob
        oracle_opt_paths = [
            '/opt/oracle/instantclient_*/lib',
            '/opt/oracle/instantclient_*',
        ]
        
        lib_dir = None
        for pattern in oracle_opt_paths:
            matches = glob.glob(pattern)
            for match in matches:
                if os.path.isdir(match):
                    lib_dir = match
                    break
            if lib_dir:
                break
        
        if lib_dir:
            try:
                oracledb.init_oracle_client(lib_dir=lib_dir, config_dir=wallet_path)
                print(f"✓ Oracle client initialized: {lib_dir} (thick mode)")
            except Exception:
                try:
                    oracledb.init_oracle_client(lib_dir=lib_dir)
                    print(f"✓ Oracle client initialized: {lib_dir} (thick mode)")
                except Exception:
                    oracledb.init_oracle_client(config_dir=wallet_path)
                    print(f"✓ Oracle client initialized (thick mode)")
        else:
            oracledb.init_oracle_client(config_dir=wallet_path)
            print(f"✓ Oracle client initialized (thick mode)")
    except Exception as e:
        print(f"⚠️  WARNING: Could not initialize Oracle client: {e}")
        print("   Attempting thin mode (limited wallet support)...")
    
    return oracledb

def get_connection():
    """Get database connection"""
    oracledb = initialize_oracle_client()
    
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    
    if not connection_string:
        print("❌ ERROR: ADB_CONNECTION_STRING not set in environment")
        sys.exit(1)
    
    if not password:
        print("❌ ERROR: ADB_PASSWORD not set in environment")
        sys.exit(1)
    
    try:
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=connection_string
        )
        print(f"✓ Connected to ADB as {username}")
        return connection
    except Exception as e:
        print(f"❌ ERROR: Could not connect to database: {e}")
        print("\nTroubleshooting:")
        print("1. Verify ADB instance is running in Oracle Cloud Console")
        print("2. Check ADB_CONNECTION_STRING format in .env")
        print("3. Verify ADB_USERNAME and ADB_PASSWORD are correct")
        print("4. Ensure wallet files are accessible")
        sys.exit(1)

def map_column_names(df):
    """Map CSV column names to Oracle table column names"""
    column_mapping = {
        'Age': 'AGE',
        'Gender': 'GENDER',
        'Country': 'COUNTRY',
        'City': 'CITY',
        'Membership_Years': 'MEMBERSHIP_YEARS',
        'Login_Frequency': 'LOGIN_FREQUENCY',
        'Session_Duration_Avg': 'SESSION_DURATION_AVG',
        'Pages_Per_Session': 'PAGES_PER_SESSION',
        'Cart_Abandonment_Rate': 'CART_ABANDONMENT_RATE',
        'Wishlist_Items': 'WISHLIST_ITEMS',
        'Total_Purchases': 'TOTAL_PURCHASES',
        'Average_Order_Value': 'AVERAGE_ORDER_VALUE',
        'Days_Since_Last_Purchase': 'DAYS_SINCE_LAST_PURCHASE',
        'Discount_Usage_Rate': 'DISCOUNT_USAGE_RATE',
        'Returns_Rate': 'RETURNS_RATE',
        'Email_Open_Rate': 'EMAIL_OPEN_RATE',
        'Customer_Service_Calls': 'CUSTOMER_SERVICE_CALLS',
        'Product_Reviews_Written': 'PRODUCT_REVIEWS_WRITTEN',
        'Social_Media_Engagement_Score': 'SOCIAL_MEDIA_ENGAGEMENT_SCORE',
        'Mobile_App_Usage': 'MOBILE_APP_USAGE',
        'Payment_Method_Diversity': 'PAYMENT_METHOD_DIVERSITY',
        'Lifetime_Value': 'LIFETIME_VALUE',
        'Credit_Balance': 'CREDIT_BALANCE',
        'Signup_Quarter': 'SIGNUP_QUARTER',
        'Churned': 'CHURNED',
        'USER_ID': 'USER_ID',  # Already uppercase in CSV
    }
    
    # Rename columns
    df_renamed = df.rename(columns=column_mapping)
    
    # Ensure all expected columns exist
    expected_cols = list(column_mapping.values())
    missing_cols = [col for col in expected_cols if col not in df_renamed.columns]
    if missing_cols:
        print(f"⚠️  WARNING: Missing columns in CSV: {missing_cols}")
    
    return df_renamed

def prepare_data_for_oracle(df):
    """Prepare DataFrame for Oracle insertion"""
    # Replace NaN with None (Oracle NULL)
    df = df.where(pd.notna(df), None)
    
    # Ensure CHURNED is integer (0 or 1)
    if 'CHURNED' in df.columns:
        df['CHURNED'] = df['CHURNED'].fillna(0).astype(int)
        # Validate CHURNED values
        invalid = df[~df['CHURNED'].isin([0, 1])]
        if len(invalid) > 0:
            print(f"⚠️  WARNING: Found {len(invalid)} rows with invalid CHURNED values")
            print("   Setting invalid values to 0")
            df.loc[~df['CHURNED'].isin([0, 1]), 'CHURNED'] = 0
    
    # Ensure USER_ID is string
    if 'USER_ID' in df.columns:
        df['USER_ID'] = df['USER_ID'].astype(str)
    
    return df

def load_training_data(connection, csv_path):
    """Load training data into CHURN_DATASET_TRAINING table"""
    print("\n" + "=" * 60)
    print("Loading Training Data")
    print("=" * 60)
    
    if not csv_path.exists():
        print(f"❌ ERROR: CSV file not found: {csv_path}")
        return False
    
    print(f"Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(df):,} rows from CSV")
    
    # Map column names
    df = map_column_names(df)
    print("✓ Mapped column names to Oracle schema")
    
    # Prepare data
    df = prepare_data_for_oracle(df)
    print("✓ Prepared data for Oracle")
    
    # Get column order matching table schema
    columns = [
        'USER_ID', 'AGE', 'GENDER', 'COUNTRY', 'CITY',
        'MEMBERSHIP_YEARS', 'LOGIN_FREQUENCY', 'SESSION_DURATION_AVG',
        'PAGES_PER_SESSION', 'CART_ABANDONMENT_RATE', 'WISHLIST_ITEMS',
        'TOTAL_PURCHASES', 'AVERAGE_ORDER_VALUE', 'DAYS_SINCE_LAST_PURCHASE',
        'DISCOUNT_USAGE_RATE', 'RETURNS_RATE', 'EMAIL_OPEN_RATE',
        'CUSTOMER_SERVICE_CALLS', 'PRODUCT_REVIEWS_WRITTEN',
        'SOCIAL_MEDIA_ENGAGEMENT_SCORE', 'MOBILE_APP_USAGE',
        'PAYMENT_METHOD_DIVERSITY', 'LIFETIME_VALUE', 'CREDIT_BALANCE',
        'SIGNUP_QUARTER', 'CHURNED'
    ]
    
    # Select only columns that exist
    available_cols = [col for col in columns if col in df.columns]
    df = df[available_cols]
    
    # Clear existing data (optional - comment out if you want to append)
    cursor = connection.cursor()
    try:
        cursor.execute("TRUNCATE TABLE OML.CHURN_DATASET_TRAINING")
        print("✓ Cleared existing training data")
    except Exception as e:
        print(f"⚠️  WARNING: Could not truncate table: {e}")
        print("   Attempting to continue...")
    
    # Insert data using executemany for performance
    print(f"\nInserting {len(df):,} rows into OML.CHURN_DATASET_TRAINING...")
    
    placeholders = ', '.join([':' + str(i+1) for i in range(len(available_cols))])
    insert_sql = f"""
        INSERT INTO OML.CHURN_DATASET_TRAINING ({', '.join(available_cols)})
        VALUES ({placeholders})
    """
    
    # Convert DataFrame to list of tuples
    data_tuples = [tuple(row) for row in df[available_cols].values]
    
    try:
        cursor.executemany(insert_sql, data_tuples)
        connection.commit()
        print(f"✓ Successfully inserted {len(df):,} rows")
        
        # Verify row count
        cursor.execute("SELECT COUNT(*) FROM OML.CHURN_DATASET_TRAINING")
        count = cursor.fetchone()[0]
        print(f"✓ Verified: {count:,} rows in table")
        return True
    except Exception as e:
        connection.rollback()
        print(f"❌ ERROR: Failed to insert data: {e}")
        return False
    finally:
        cursor.close()

def load_user_profiles(connection, csv_path):
    """Load user profiles into USER_PROFILES table"""
    print("\n" + "=" * 60)
    print("Loading User Profiles")
    print("=" * 60)
    
    if not csv_path.exists():
        print(f"❌ ERROR: CSV file not found: {csv_path}")
        return False
    
    print(f"Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(df):,} rows from CSV")
    
    # Map column names
    df = map_column_names(df)
    print("✓ Mapped column names to Oracle schema")
    
    # Prepare data
    df = prepare_data_for_oracle(df)
    print("✓ Prepared data for Oracle")
    
    # Get column order matching table schema
    columns = [
        'USER_ID', 'AGE', 'GENDER', 'COUNTRY', 'CITY',
        'MEMBERSHIP_YEARS', 'LOGIN_FREQUENCY', 'SESSION_DURATION_AVG',
        'PAGES_PER_SESSION', 'CART_ABANDONMENT_RATE', 'WISHLIST_ITEMS',
        'TOTAL_PURCHASES', 'AVERAGE_ORDER_VALUE', 'DAYS_SINCE_LAST_PURCHASE',
        'DISCOUNT_USAGE_RATE', 'RETURNS_RATE', 'EMAIL_OPEN_RATE',
        'CUSTOMER_SERVICE_CALLS', 'PRODUCT_REVIEWS_WRITTEN',
        'SOCIAL_MEDIA_ENGAGEMENT_SCORE', 'MOBILE_APP_USAGE',
        'PAYMENT_METHOD_DIVERSITY', 'LIFETIME_VALUE', 'CREDIT_BALANCE',
        'SIGNUP_QUARTER', 'CHURNED'
    ]
    
    # Select only columns that exist
    available_cols = [col for col in columns if col in df.columns]
    df = df[available_cols]
    
    # Clear existing data (optional - comment out if you want to append)
    cursor = connection.cursor()
    try:
        cursor.execute("TRUNCATE TABLE OML.USER_PROFILES")
        print("✓ Cleared existing user profiles")
    except Exception as e:
        print(f"⚠️  WARNING: Could not truncate table: {e}")
        print("   Attempting to continue...")
    
    # Insert data using executemany for performance
    print(f"\nInserting {len(df):,} rows into OML.USER_PROFILES...")
    
    placeholders = ', '.join([':' + str(i+1) for i in range(len(available_cols))])
    insert_sql = f"""
        INSERT INTO OML.USER_PROFILES ({', '.join(available_cols)})
        VALUES ({placeholders})
    """
    
    # Convert DataFrame to list of tuples
    data_tuples = [tuple(row) for row in df[available_cols].values]
    
    try:
        cursor.executemany(insert_sql, data_tuples)
        connection.commit()
        print(f"✓ Successfully inserted {len(df):,} rows")
        
        # Verify row count
        cursor.execute("SELECT COUNT(*) FROM OML.USER_PROFILES")
        count = cursor.fetchone()[0]
        print(f"✓ Verified: {count:,} rows in table")
        return True
    except Exception as e:
        connection.rollback()
        print(f"❌ ERROR: Failed to insert data: {e}")
        return False
    finally:
        cursor.close()

def main():
    """Main function"""
    print("=" * 60)
    print("Churn Data Ingestion Script")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define CSV file paths
    training_csv = project_root / 'data' / 'processed' / 'churn_dataset_training.csv'
    user_profiles_csv = project_root / 'data' / 'processed' / 'churn_dataset_mapped.csv'
    
    # Check if CSV files exist
    if not training_csv.exists():
        print(f"❌ ERROR: Training CSV not found: {training_csv}")
        sys.exit(1)
    
    if not user_profiles_csv.exists():
        print(f"❌ ERROR: User profiles CSV not found: {user_profiles_csv}")
        sys.exit(1)
    
    # Connect to database
    connection = get_connection()
    
    try:
        # Load training data
        training_success = load_training_data(connection, training_csv)
        
        # Load user profiles
        profiles_success = load_user_profiles(connection, user_profiles_csv)
        
        # Summary
        print("\n" + "=" * 60)
        print("Ingestion Summary")
        print("=" * 60)
        print(f"Training Data:    {'✓ SUCCESS' if training_success else '❌ FAILED'}")
        print(f"User Profiles:    {'✓ SUCCESS' if profiles_success else '❌ FAILED'}")
        
        if training_success and profiles_success:
            print("\n✓ All data loaded successfully!")
            print("\nNext steps:")
            print("1. Validate data (Task 2.6)")
            print("2. Create feature engineering views (Task 2.7)")
            print("3. Train model (Task 3.x)")
        else:
            print("\n⚠️  Some data failed to load. Check errors above.")
            sys.exit(1)
    
    finally:
        connection.close()
        print(f"\n✓ Connection closed")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
