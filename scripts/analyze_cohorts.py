#!/usr/bin/env python3
"""
Analyze Cohort Distribution and At-Risk Users
Based on current cohort definitions in docs/COHORT_DEFINITIONS.md
"""

import os
import sys
from pathlib import Path
import glob
from dotenv import load_dotenv

env_file = Path('.env')
if env_file.exists():
    load_dotenv(dotenv_path=env_file)

import oracledb

wallet_path = os.getenv('ADB_WALLET_PATH')
if not os.getenv('TNS_ADMIN'):
    os.environ['TNS_ADMIN'] = wallet_path

try:
    oracle_opt_paths = ['/opt/oracle/instantclient_*/lib', '/opt/oracle/instantclient_*']
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
        except:
            try:
                oracledb.init_oracle_client(lib_dir=lib_dir)
            except:
                oracledb.init_oracle_client(config_dir=wallet_path)
    else:
        oracledb.init_oracle_client(config_dir=wallet_path)
except:
    pass

conn = oracledb.connect(
    user=os.getenv('ADB_USERNAME', 'OML'),
    password=os.getenv('ADB_PASSWORD'),
    dsn=os.getenv('ADB_CONNECTION_STRING')
)

cursor = conn.cursor()

print('=' * 80)
print('Cohort Analysis: Total Users and At-Risk Users')
print('=' * 80)
print()

# Get total users
cursor.execute('SELECT COUNT(*) FROM OML.USER_PROFILES')
total_users = cursor.fetchone()[0]
print(f'Total Users: {total_users:,}')
print()

# VIP Cohort: LIFETIME_VALUE > $5,000 OR MEMBERSHIP_YEARS > 5
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) as at_risk
    FROM OML.USER_PROFILES up
    LEFT JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
    WHERE (up.LIFETIME_VALUE > 5000 OR up.MEMBERSHIP_YEARS > 5)
''')
vip_total, vip_at_risk = cursor.fetchone()

# New Cohort: NOT VIP AND MEMBERSHIP_YEARS < 1
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) as at_risk
    FROM OML.USER_PROFILES up
    LEFT JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
    WHERE NOT (up.LIFETIME_VALUE > 5000 OR up.MEMBERSHIP_YEARS > 5)  -- Not VIP
      AND up.MEMBERSHIP_YEARS < 1  -- Less than 1 year
''')
new_total, new_at_risk = cursor.fetchone()

# Dormant Cohort: NOT VIP, NOT New, AND (DAYS_SINCE_LAST_PURCHASE > 90 OR LOGIN_FREQUENCY = 0)
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) as at_risk
    FROM OML.USER_PROFILES up
    LEFT JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
    WHERE NOT (up.LIFETIME_VALUE > 5000 OR up.MEMBERSHIP_YEARS > 5)  -- Not VIP
      AND up.MEMBERSHIP_YEARS >= 1  -- Not New (membership >= 1 year)
      AND (up.DAYS_SINCE_LAST_PURCHASE > 90 OR up.LOGIN_FREQUENCY = 0)  -- Dormant
''')
dormant_total, dormant_at_risk = cursor.fetchone()

# At-Risk Cohort: PREDICTED_CHURN_PROBABILITY >= 0.42 (optimal threshold) OR PREDICTED_CHURN_LABEL = 1
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) as at_risk
    FROM OML.USER_PROFILES up
    INNER JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
    WHERE (cp.PREDICTED_CHURN_PROBABILITY >= 0.42 OR cp.PREDICTED_CHURN_LABEL = 1)
''')
atrisk_total, atrisk_at_risk = cursor.fetchone()

# Regular Cohort: Not VIP, not New, not Dormant (and active)
# This is the default/remaining cohort
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) as at_risk
    FROM OML.USER_PROFILES up
    LEFT JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
    WHERE NOT (up.LIFETIME_VALUE > 5000 OR up.MEMBERSHIP_YEARS > 5)  -- Not VIP
      AND up.MEMBERSHIP_YEARS >= 1  -- Not New (membership >= 1 year)
      AND NOT (up.DAYS_SINCE_LAST_PURCHASE > 90 OR up.LOGIN_FREQUENCY = 0)  -- Not Dormant
      AND up.TOTAL_PURCHASES >= 2  -- Has made purchases
      AND up.DAYS_SINCE_LAST_PURCHASE <= 90  -- Active in last 90 days
      AND up.LOGIN_FREQUENCY > 0  -- Has logged in
''')
regular_total, regular_at_risk = cursor.fetchone()

# Print results
print('Cohort Distribution:')
print('-' * 80)
print(f'{"Cohort":<20} {"Total Users":<15} {"At-Risk":<15} {"At-Risk %":<15} {"Safe":<15}')
print('-' * 80)

cohorts = [
    ('VIP', vip_total, vip_at_risk),
    ('New', new_total, new_at_risk),
    ('Dormant', dormant_total, dormant_at_risk),
    ('At-Risk', atrisk_total, atrisk_at_risk),
    ('Regular', regular_total, regular_at_risk),
]

for name, total, at_risk in cohorts:
    safe = total - at_risk if total else 0
    at_risk_pct = (at_risk / total * 100) if total > 0 else 0
    print(f'{name:<20} {total:<15,} {at_risk:<15,} {at_risk_pct:<14.1f}% {safe:<15,}')

# Get actual total at-risk (not sum of cohorts, which would double-count)
cursor.execute('''
    SELECT COUNT(*)
    FROM OML.CHURN_PREDICTIONS
    WHERE PREDICTED_CHURN_LABEL = 1
''')
actual_at_risk_total = cursor.fetchone()[0]

print('-' * 80)
print(f'{"TOTAL":<20} {total_users:<15,} {actual_at_risk_total:<15,} {actual_at_risk_total/total_users*100:<14.1f}% {total_users - actual_at_risk_total:<15,}')
print()
print('Note: Cohort totals may sum to more than 5,003 due to overlap (e.g., VIP + At-Risk)')
print()

# Verify overlap (users can be in multiple cohorts)
print('=' * 80)
print('Cohort Overlap Analysis')
print('=' * 80)
print()

# Check VIP + At-Risk overlap
cursor.execute('''
    SELECT COUNT(*)
    FROM OML.USER_PROFILES up
    INNER JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
    WHERE (up.LIFETIME_VALUE > 5000 OR up.MEMBERSHIP_YEARS > 5)
      AND (cp.PREDICTED_CHURN_PROBABILITY >= 0.42 OR cp.PREDICTED_CHURN_LABEL = 1)
''')
vip_atrisk_overlap = cursor.fetchone()[0]

# Check New + At-Risk overlap
cursor.execute('''
    SELECT COUNT(*)
    FROM OML.USER_PROFILES up
    INNER JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
    WHERE NOT (up.LIFETIME_VALUE > 5000 OR up.MEMBERSHIP_YEARS > 5)  -- Not VIP
      AND up.MEMBERSHIP_YEARS < 1  -- New
      AND (cp.PREDICTED_CHURN_PROBABILITY >= 0.42 OR cp.PREDICTED_CHURN_LABEL = 1)  -- At-Risk
''')
new_atrisk_overlap = cursor.fetchone()[0]

# Check Dormant + At-Risk overlap
cursor.execute('''
    SELECT COUNT(*)
    FROM OML.USER_PROFILES up
    INNER JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
    WHERE NOT (up.LIFETIME_VALUE > 5000 OR up.MEMBERSHIP_YEARS > 5)  -- Not VIP
      AND up.MEMBERSHIP_YEARS >= 1  -- Not New
      AND (up.DAYS_SINCE_LAST_PURCHASE > 90 OR up.LOGIN_FREQUENCY = 0)  -- Dormant
      AND (cp.PREDICTED_CHURN_PROBABILITY >= 0.42 OR cp.PREDICTED_CHURN_LABEL = 1)  -- At-Risk
''')
dormant_atrisk_overlap = cursor.fetchone()[0]

print('Note: Cohorts can overlap (e.g., a user can be both VIP and At-Risk)')
print()
print(f'VIP + At-Risk overlap: {vip_atrisk_overlap:,} users')
print(f'New + At-Risk overlap: {new_atrisk_overlap:,} users')
print(f'Dormant + At-Risk overlap: {dormant_atrisk_overlap:,} users')
print()

# Summary statistics
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN cp.PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) as at_risk,
        AVG(cp.PREDICTED_CHURN_PROBABILITY) as avg_prob,
        AVG(cp.RISK_SCORE) as avg_risk
    FROM OML.USER_PROFILES up
    INNER JOIN OML.CHURN_PREDICTIONS cp ON up.USER_ID = cp.USER_ID
''')
overall_total, overall_at_risk, avg_prob, avg_risk = cursor.fetchone()

print('=' * 80)
print('Overall Statistics')
print('=' * 80)
print(f'Total users with predictions: {overall_total:,}')
print(f'Total at-risk users: {overall_at_risk:,} ({overall_at_risk/overall_total*100:.1f}%)')
print(f'Average churn probability: {avg_prob:.4f} ({avg_prob*100:.2f}%)')
print(f'Average risk score: {avg_risk:.1f}')

cursor.close()
conn.close()
