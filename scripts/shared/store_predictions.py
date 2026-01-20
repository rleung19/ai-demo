#!/usr/bin/env python3
"""
Shared utility for storing predictions in CHURN_PREDICTIONS table
Used by both OML4Py and local model scoring scripts
"""

from datetime import datetime
import pandas as pd
import numpy as np

def store_predictions(connection, user_ids, churn_probabilities, model_version='v1.0', threshold=0.5):
    """Store predictions in CHURN_PREDICTIONS table"""
    print("\n" + "=" * 60)
    print("Storing Predictions")
    print("=" * 60)
    
    import oracledb
    
    # Calculate predictions
    predicted_labels = (churn_probabilities >= threshold).astype(int)
    risk_scores = (churn_probabilities * 100).astype(int).clip(0, 100)
    
    # Prepare data for insertion
    prediction_date = datetime.now()
    
    cursor = connection.cursor()
    
    # Clear existing predictions (optional - comment out to append)
    try:
        cursor.execute("TRUNCATE TABLE OML.CHURN_PREDICTIONS")
        print("✓ Cleared existing predictions")
    except Exception as e:
        print(f"⚠️  WARNING: Could not truncate table: {e}")
    
    # Insert predictions
    print(f"\nInserting {len(user_ids):,} predictions...")
    
    insert_sql = """
        INSERT INTO OML.CHURN_PREDICTIONS (
            USER_ID,
            PREDICTED_CHURN_PROBABILITY,
            PREDICTED_CHURN_LABEL,
            RISK_SCORE,
            MODEL_VERSION,
            PREDICTION_DATE
        ) VALUES (:1, :2, :3, :4, :5, :6)
    """
    
    data_tuples = []
    for i in range(len(user_ids)):
        data_tuples.append((
            str(user_ids.iloc[i]) if isinstance(user_ids, pd.Series) else str(user_ids[i]),
            float(churn_probabilities[i]),
            int(predicted_labels[i]),
            int(risk_scores[i]),
            model_version,
            prediction_date
        ))
    
    try:
        cursor.executemany(insert_sql, data_tuples)
        connection.commit()
        print(f"✓ Successfully inserted {len(data_tuples):,} predictions")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM OML.CHURN_PREDICTIONS")
        count = cursor.fetchone()[0]
        print(f"✓ Verified: {count:,} rows in CHURN_PREDICTIONS table")
        
        # Summary statistics
        cursor.execute("""
            SELECT 
                COUNT(*) AS TOTAL,
                SUM(CASE WHEN PREDICTED_CHURN_LABEL = 1 THEN 1 ELSE 0 END) AS AT_RISK,
                AVG(PREDICTED_CHURN_PROBABILITY) * 100 AS AVG_RISK_SCORE,
                AVG(RISK_SCORE) AS AVG_RISK_SCORE_INT
            FROM OML.CHURN_PREDICTIONS
        """)
        stats = cursor.fetchone()
        total, at_risk, avg_prob, avg_risk = stats
        
        print(f"\nPrediction Summary:")
        print(f"  Total users: {total:,}")
        print(f"  At-risk users: {at_risk:,} ({at_risk/total*100:.2f}%)")
        print(f"  Average risk score: {avg_risk:.1f}%")
        
        return True
    except Exception as e:
        connection.rollback()
        print(f"❌ ERROR: Failed to insert predictions: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
