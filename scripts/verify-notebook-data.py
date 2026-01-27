#!/usr/bin/env python3
"""
Verify database access and check tables/views used in the Recommender notebook
"""

import os
import sys
from pathlib import Path

# Find project root and load .env
script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / '.env'

try:
    from dotenv import load_dotenv
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        print(f"✓ Loaded .env from: {env_file}\n")
    else:
        print(f"❌ .env file not found at {env_file}")
        sys.exit(1)
except ImportError:
    print("❌ python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

try:
    import oracledb
    print("✓ oracledb module imported\n")
except ImportError:
    print("❌ oracledb not installed. Run: pip install oracledb")
    sys.exit(1)

def test_connection():
    """Test database connection and query notebook tables/views"""
    
    print("=" * 70)
    print("DATABASE CONNECTION TEST")
    print("=" * 70)
    
    # Get connection parameters
    wallet_path = os.getenv('ADB_WALLET_PATH')
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    
    print(f"Wallet Path: {wallet_path}")
    print(f"Connection String: {connection_string}")
    print(f"Username: {username}")
    print(f"Password: {'*' * 8 if password else 'NOT SET'}")
    print()
    
    if not all([wallet_path, connection_string, username, password]):
        print("❌ Missing required environment variables")
        return False
    
    # Set TNS_ADMIN
    os.environ['TNS_ADMIN'] = wallet_path
    
    try:
        # Try to initialize thick mode (with Instant Client)
        try:
            # Try common locations for Oracle Instant Client
            import glob
            possible_paths = [
                '/opt/oracle/instantclient_*',
                '/opt/homebrew/lib',
                '/usr/local/lib',
            ]
            
            lib_dir = None
            for pattern in possible_paths:
                matches = glob.glob(pattern) if '*' in pattern else [pattern]
                for match in matches:
                    if os.path.exists(match):
                        # Check for library file
                        for lib_name in ['libclntsh.dylib', 'libclntsh.so']:
                            lib_path = os.path.join(match, lib_name)
                            if os.path.exists(lib_path):
                                lib_dir = match
                                break
                        if lib_dir:
                            break
                if lib_dir:
                    break
            
            if lib_dir:
                oracledb.init_oracle_client(lib_dir=lib_dir)
                print(f"✓ Oracle Instant Client initialized (thick mode): {lib_dir}\n")
            else:
                print("⚠️  Oracle Instant Client not found, using thin mode")
                print("   (Thin mode may have limited wallet support)\n")
        except Exception as e:
            print(f"⚠️  Thick mode initialization failed: {e}")
            print("   Using thin mode\n")
        
        # Connect to database
        print(f"Connecting to {connection_string}...")
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=connection_string
        )
        print("✓ Successfully connected to database!\n")
        
        cursor = connection.cursor()
        
        # Test basic query
        print("-" * 70)
        print("TEST 1: Basic Query (SELECT 1 FROM DUAL)")
        print("-" * 70)
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        print(f"✓ Result: {result[0]}\n")
        
        # Check current user
        print("-" * 70)
        print("TEST 2: Current User")
        print("-" * 70)
        cursor.execute("SELECT USER FROM DUAL")
        current_user = cursor.fetchone()[0]
        print(f"✓ Connected as: {current_user}\n")
        
        # Check access to ADMIN.ORDERS_PROFILE_V (from notebook)
        print("=" * 70)
        print("NOTEBOOK TABLE/VIEW VERIFICATION")
        print("=" * 70)
        print("\nThe notebook accessed: ADMIN.ORDERS_PROFILE_V")
        print()
        
        # Test if we can access ADMIN.ORDERS_PROFILE_V
        print("-" * 70)
        print("TEST 3: Access to ADMIN.ORDERS_PROFILE_V")
        print("-" * 70)
        
        try:
            # Check row count
            cursor.execute("SELECT COUNT(*) FROM ADMIN.ORDERS_PROFILE_V")
            total_rows = cursor.fetchone()[0]
            print(f"✓ Can access ADMIN.ORDERS_PROFILE_V")
            print(f"✓ Total rows: {total_rows:,}\n")
            
            # Get sample columns
            cursor.execute("""
                SELECT * FROM ADMIN.ORDERS_PROFILE_V 
                WHERE ROWNUM <= 1
            """)
            columns = [col[0] for col in cursor.description]
            print(f"✓ Total columns: {len(columns)}")
            print(f"✓ Sample columns: {', '.join(columns[:10])}{'...' if len(columns) > 10 else ''}\n")
            
            # Check distinct counts for key fields used in notebook
            print("-" * 70)
            print("TEST 4: Data Statistics (from notebook queries)")
            print("-" * 70)
            
            # User count
            cursor.execute("""
                SELECT COUNT(DISTINCT USER_ID) 
                FROM ADMIN.ORDERS_PROFILE_V
                WHERE USER_ID IS NOT NULL
            """)
            user_count = cursor.fetchone()[0]
            print(f"✓ Distinct users (USER_ID): {user_count:,}")
            
            # Product count
            cursor.execute("""
                SELECT COUNT(DISTINCT PRODUCT_ID) 
                FROM ADMIN.ORDERS_PROFILE_V
                WHERE PRODUCT_ID IS NOT NULL
            """)
            product_count = cursor.fetchone()[0]
            print(f"✓ Distinct products (PRODUCT_ID): {product_count:,}")
            
            # Interactions with ratings
            cursor.execute("""
                SELECT COUNT(*) 
                FROM ADMIN.ORDERS_PROFILE_V
                WHERE RATING IS NOT NULL
            """)
            interaction_count = cursor.fetchone()[0]
            print(f"✓ Interactions with ratings: {interaction_count:,}")
            
            print("\n" + "-" * 70)
            print("COMPARISON WITH NOTEBOOK TRAINING DATA")
            print("-" * 70)
            print(f"Notebook trained with:")
            print(f"  - 26 users")
            print(f"  - 84 products")
            print(f"  - 56 interactions with ratings")
            print()
            print(f"Current database has:")
            print(f"  - {user_count:,} users ({'+' if user_count > 26 else ''}{user_count - 26} change)")
            print(f"  - {product_count:,} products ({'+' if product_count > 84 else ''}{product_count - 84} change)")
            print(f"  - {interaction_count:,} interactions ({'+' if interaction_count > 56 else ''}{interaction_count - 56} change)")
            
            if user_count > 26 or product_count > 84 or interaction_count > 56:
                print("\n✓ NEW DATA AVAILABLE - Model can be retrained with more data!")
            else:
                print("\n⚠️  No new data since training")
            
        except Exception as e:
            print(f"❌ Error accessing ADMIN.ORDERS_PROFILE_V: {e}")
            print("\nPossible reasons:")
            print("1. View does not exist")
            print("2. OML user doesn't have SELECT privilege on ADMIN.ORDERS_PROFILE_V")
            print("3. View is in a different schema")
            return False
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Verify ADB instance is running")
        print("2. Check wallet files are correct")
        print("3. Verify credentials are correct")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
