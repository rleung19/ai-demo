#!/usr/bin/env python3
"""
Complete ML Pipeline: Train/Test/Deploy Workflow
Task 3.9: Create automated pipeline script (train/test/deploy workflow)

This script orchestrates the complete ML pipeline:
1. Train model (Tasks 3.1-3.7)
2. Score users (Task 3.8)
3. Generate summary report

Usage:
    # In OML Notebooks (recommended):
    %python
    exec(open('scripts/ml_pipeline.py').read())
    
    # Or run as standalone (requires OML4Py):
    python scripts/ml_pipeline.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Import training and scoring functions
script_dir = Path(__file__).parent

def main():
    """Main pipeline orchestration"""
    print("=" * 60)
    print("Complete ML Pipeline: Train/Test/Deploy")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Import training script
    print("\n" + "=" * 60)
    print("Phase 1: Model Training")
    print("=" * 60)
    
    try:
        # Import and run training
        sys.path.insert(0, str(script_dir))
        from train_churn_model import main as train_main
        
        train_results = train_main()
        
        if train_results is None:
            print("❌ Training failed")
            sys.exit(1)
        
        print("\n✓ Training phase completed")
        
    except Exception as e:
        print(f"❌ ERROR: Training phase failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Import and run scoring
    print("\n" + "=" * 60)
    print("Phase 2: Model Scoring")
    print("=" * 60)
    
    try:
        from score_churn_model import main as score_main
        score_main()
        print("\n✓ Scoring phase completed")
        
    except Exception as e:
        print(f"❌ ERROR: Scoring phase failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("Pipeline Summary")
    print("=" * 60)
    print("✓ Model trained and saved to OML datastore")
    print("✓ Users scored and predictions stored")
    print("✓ Ready for API integration")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
