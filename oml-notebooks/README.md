# OML Notebooks for Churn Analysis

This directory contains OML Notebook JSON files ready to import into Oracle Machine Learning Notebooks on Oracle Autonomous Database.

## Files

1. **`churn_analysis_complete.ipynb`** ⭐ **RECOMMENDED** - Complete notebook with both original and enhanced models (27 paragraphs total)
2. **`churn_analysis_original.ipynb`** - Original model workflow only (baseline, 13 steps)
3. **`churn_analysis_enhanced.md`** - Enhanced model workflow (markdown format for reference)

## Prerequisites

- Oracle Autonomous Database (Serverless) with OML enabled
- ADMIN schema with required tables:
  - `USERS`, `ORDERS`, `ORDER_ITEMS`, `LOGIN_EVENTS`
  - `PRODUCT_REVIEWS`, `EMAIL_ENGAGEMENT`, `CART_EVENTS`, `RETURNS`
- OML schema access (for creating views and storing models)
- OML Notebooks UI access

## Import Instructions

1. **Access OML Notebooks**:
   - Log into Oracle Cloud Console
   - Navigate to your ADB instance
   - Open OML Notebooks UI

2. **Import Notebook**:
   - Click "Import" or "Upload Notebook"
   - **Recommended**: Select `churn_analysis_complete.ipynb` (contains both original and enhanced models)
   - Or select individual files: `churn_analysis_original.ipynb` for baseline only
   - **Note**: If OML Notebooks requires `.json` format, you may need to rename back to `.json` or check OML Notebooks import options
   - Wait for import to complete

3. **Run Notebook**:
   - Execute cells sequentially (top to bottom)
   - Each cell is marked with its step number
   - Review outputs before proceeding to next step

## Execution Order

### Complete Notebook (Recommended)
The `churn_analysis_complete.ipynb` file contains both workflows:
1. **Phase 1**: Original Model (Steps 1-13) - Run first to establish baseline
2. **Phase 2**: Enhanced Model (Enhanced Steps 1-8) - Run after Phase 1 to see improvements

### Original Model Workflow
1. Step 1: Create Database Views
2. Step 2: Check OML4Py Connection
3. Step 3: Explore Data
4. Step 4: Prepare Features and Split Data
5. Step 5: Train XGBoost Model
6. Step 6: Evaluate Model
7. Step 7: Feature Importance
8. Step 8: Save Model
9. Step 9: Optimize Threshold
10. Step 10: Score All Customers
11. Step 11: Cohort-Level Metrics
12. Step 12: Analyze Risk Factors
13. Step 13: Summary Report

### Enhanced Model Workflow
1. Step 1: Create Enhanced Features View
2. Step 2: Create Enhanced Training Data View
3. Step 3: Verify Enhanced Views
4. Step 4: Prepare Features and Split Data (with categorical encoding)
5. Step 5: Train Enhanced Model
6. Step 6: Evaluate Enhanced Model
7. Step 7: Feature Importance (Enhanced)
8. Step 8: Summary and Comparison

## Notes

- **Categorical Features**: The enhanced model includes categorical features converted to numeric codes
- **Feature Engineering**: Enhanced model includes 17 new engineered features
- **Model Comparison**: Step 7 in enhanced workflow compares with original model
- **Threshold**: Both models use optimized threshold (0.1) instead of default 0.5

## Troubleshooting

- **Connection Issues**: Verify OML connection in Step 2
- **View Creation Errors**: Check schema permissions (OML schema needs CREATE VIEW privilege)
- **Model Training Errors**: Ensure training data has sufficient samples (>1000 recommended)
- **Prediction Errors**: Verify test data has same features as training data

## Support

Refer to `PROPOSAL.md` for detailed documentation and business context.
