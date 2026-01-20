#!/usr/bin/env python3
"""
Check VIP Users Count
Quick script to check how many VIP users exist based on current definition
"""

import os
import sys
from pathlib import Path
import glob

# Find project root
script_dir = Path(__file__).parent
project_root = script_dir.parent
env_file = project_root / '.env'

# Load environment variables
try:
    from dotenv import load_dotenv
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
except ImportError:
    pass

def initialize_oracle_client():
    """Initialize Oracle client"""
    try:
        import oracledb
    except ImportError:
        print("❌ ERROR: oracledb not installed")
        sys.exit(1)
    
    wallet_path = os.getenv('ADB_WALLET_PATH')
    if not wallet_path or not os.path.exists(wallet_path):
        print("❌ ERROR: ADB_WALLET_PATH not set or invalid")
        sys.exit(1)
    
    if not os.getenv('TNS_ADMIN'):
        os.environ['TNS_ADMIN'] = wallet_path
    
    try:
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
            except Exception:
                try:
                    oracledb.init_oracle_client(lib_dir=lib_dir)
                except Exception:
                    oracledb.init_oracle_client(config_dir=wallet_path)
        else:
            oracledb.init_oracle_client(config_dir=wallet_path)
    except Exception:
        pass
    
    return oracledb

def get_connection():
    """Get database connection"""
    oracledb = initialize_oracle_client()
    connection_string = os.getenv('ADB_CONNECTION_STRING')
    username = os.getenv('ADB_USERNAME', 'OML')
    password = os.getenv('ADB_PASSWORD')
    
    if not connection_string or not password:
        print("❌ ERROR: ADB connection credentials not set")
        sys.exit(1)
    
    try:
        return oracledb.connect(user=username, password=password, dsn=connection_string)
    except Exception as e:
        print(f"❌ ERROR: Failed to connect: {e}")
        sys.exit(1)

def check_vip_users(connection):
    """Check VIP users based on current definition"""
    cursor = connection.cursor()
    
    print("=" * 60)
    print("VIP Users Analysis")
    print("=" * 60)
    print("\nVIP Definition:")
    print("  LIFETIME_VALUE > 5000 OR MEMBERSHIP_YEARS > 5")
    print("  (Updated from $10,000 threshold - see analysis below)")
    
    # Check total users
    cursor.execute("SELECT COUNT(*) FROM OML.USER_PROFILES")
    total_users = cursor.fetchone()[0]
    print(f"\nTotal users: {total_users:,}")
    
    # Check VIP by LTV (old threshold)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM OML.USER_PROFILES 
        WHERE LIFETIME_VALUE > 10000
    """)
    vip_by_ltv_old = cursor.fetchone()[0]
    print(f"\nVIP by LIFETIME_VALUE > 10000 (old): {vip_by_ltv_old:,}")
    
    # Check VIP by LTV (new threshold)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM OML.USER_PROFILES 
        WHERE LIFETIME_VALUE > 5000
    """)
    vip_by_ltv = cursor.fetchone()[0]
    print(f"VIP by LIFETIME_VALUE > 5000 (new): {vip_by_ltv:,}")
    
    # Check VIP by membership
    cursor.execute("""
        SELECT COUNT(*) 
        FROM OML.USER_PROFILES 
        WHERE MEMBERSHIP_YEARS > 5
    """)
    vip_by_membership = cursor.fetchone()[0]
    print(f"VIP by MEMBERSHIP_YEARS > 5: {vip_by_membership:,}")
    
    # Check VIP total (either condition with new threshold)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM OML.USER_PROFILES 
        WHERE LIFETIME_VALUE > 5000 OR MEMBERSHIP_YEARS > 5
    """)
    vip_total = cursor.fetchone()[0]
    print(f"\nTotal VIP users (LTV > 5000 OR Years > 5): {vip_total:,} ({vip_total/total_users*100:.2f}%)")
    
    # Check overlap
    cursor.execute("""
        SELECT COUNT(*) 
        FROM OML.USER_PROFILES 
        WHERE LIFETIME_VALUE > 5000 AND MEMBERSHIP_YEARS > 5
    """)
    vip_both = cursor.fetchone()[0]
    print(f"VIP by both conditions: {vip_both:,}")
    
    # Distribution stats
    print("\n" + "=" * 60)
    print("LIFETIME_VALUE Distribution")
    print("=" * 60)
    cursor.execute("""
        SELECT 
            MIN(LIFETIME_VALUE) AS min_ltv,
            MAX(LIFETIME_VALUE) AS max_ltv,
            AVG(LIFETIME_VALUE) AS avg_ltv,
            MEDIAN(LIFETIME_VALUE) AS median_ltv,
            COUNT(CASE WHEN LIFETIME_VALUE > 10000 THEN 1 END) AS above_10k,
            COUNT(CASE WHEN LIFETIME_VALUE > 5000 THEN 1 END) AS above_5k,
            COUNT(CASE WHEN LIFETIME_VALUE > 1000 THEN 1 END) AS above_1k
        FROM OML.USER_PROFILES
    """)
    stats = cursor.fetchone()
    min_ltv, max_ltv, avg_ltv, median_ltv, above_10k, above_5k, above_1k = stats
    print(f"Min LTV: ${min_ltv:,.2f}")
    print(f"Max LTV: ${max_ltv:,.2f}")
    print(f"Avg LTV: ${avg_ltv:,.2f}")
    print(f"Median LTV: ${median_ltv:,.2f}")
    print(f"\nDistribution:")
    print(f"  > $10,000: {above_10k:,} ({above_10k/total_users*100:.2f}%)")
    print(f"  > $5,000:  {above_5k:,} ({above_5k/total_users*100:.2f}%)")
    print(f"  > $1,000:  {above_1k:,} ({above_1k/total_users*100:.2f}%)")
    
    print("\n" + "=" * 60)
    print("MEMBERSHIP_YEARS Distribution")
    print("=" * 60)
    cursor.execute("""
        SELECT 
            MIN(MEMBERSHIP_YEARS) AS min_years,
            MAX(MEMBERSHIP_YEARS) AS max_years,
            AVG(MEMBERSHIP_YEARS) AS avg_years,
            MEDIAN(MEMBERSHIP_YEARS) AS median_years,
            COUNT(CASE WHEN MEMBERSHIP_YEARS > 5 THEN 1 END) AS above_5_years,
            COUNT(CASE WHEN MEMBERSHIP_YEARS > 3 THEN 1 END) AS above_3_years,
            COUNT(CASE WHEN MEMBERSHIP_YEARS > 1 THEN 1 END) AS above_1_year
        FROM OML.USER_PROFILES
    """)
    stats = cursor.fetchone()
    min_years, max_years, avg_years, median_years, above_5_years, above_3_years, above_1_year = stats
    print(f"Min years: {min_years:.2f}")
    print(f"Max years: {max_years:.2f}")
    print(f"Avg years: {avg_years:.2f}")
    print(f"Median years: {median_years:.2f}")
    print(f"\nDistribution:")
    print(f"  > 5 years: {above_5_years:,} ({above_5_years/total_users*100:.2f}%)")
    print(f"  > 3 years: {above_3_years:,} ({above_3_years/total_users*100:.2f}%)")
    print(f"  > 1 year:  {above_1_year:,} ({above_1_year/total_users*100:.2f}%)")
    
    # Sample VIP users
    print("\n" + "=" * 60)
    print("Sample VIP Users (first 10)")
    print("=" * 60)
    cursor.execute("""
        SELECT 
            USER_ID,
            LIFETIME_VALUE,
            MEMBERSHIP_YEARS,
            TOTAL_PURCHASES,
            CASE 
                WHEN LIFETIME_VALUE > 5000 AND MEMBERSHIP_YEARS > 5 THEN 'Both'
                WHEN LIFETIME_VALUE > 5000 THEN 'LTV'
                WHEN MEMBERSHIP_YEARS > 5 THEN 'Membership'
            END AS vip_reason
        FROM OML.USER_PROFILES 
        WHERE LIFETIME_VALUE > 5000 OR MEMBERSHIP_YEARS > 5
        ORDER BY LIFETIME_VALUE DESC
        FETCH FIRST 10 ROWS ONLY
    """)
    print(f"{'USER_ID':<36} {'LTV':>12} {'Years':>8} {'Purchases':>10} {'Reason':>12}")
    print("-" * 80)
    for row in cursor.fetchall():
        user_id, ltv, years, purchases, reason = row
        print(f"{user_id:<36} ${ltv:>11,.2f} {years:>7.2f} {purchases:>10} {reason:>12}")
    
    cursor.close()
    
    return vip_total

def main():
    """Main function"""
    connection = get_connection()
    
    try:
        vip_count = check_vip_users(connection)
        print(f"\n✓ Analysis complete")
        print(f"  Total VIP users: {vip_count:,}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        connection.close()

if __name__ == '__main__':
    main()
