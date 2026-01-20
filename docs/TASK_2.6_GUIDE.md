# Task 2.6: Validate Data Loaded Correctly

## Status

✅ **Completed**: Data validation script created and executed successfully

## What Was Created

### Validation Script
- **File**: `scripts/validate_churn_data.py`
- **Purpose**: Comprehensive validation of loaded data

### Validation Checks

1. **Row Count Validation**
   - Verifies expected row counts match actual
   - `CHURN_DATASET_TRAINING`: 45,858 rows ✓
   - `USER_PROFILES`: 4,142 rows ✓

2. **Data Type Validation**
   - CHURNED values are 0 or 1
   - USER_ID is NOT NULL
   - Data types match schema

3. **Constraint Validation**
   - CHURNED constraint (0 or 1) enforced
   - USER_ID NOT NULL constraint
   - USER_ID uniqueness constraint

4. **Data Quality Validation**
   - Churn rate within expected range (10-50%)
   - Training data: 28.87% churn rate ✓
   - User profiles: 28.9% churn rate ✓
   - Data ranges valid (AGE, TOTAL_PURCHASES, LIFETIME_VALUE)

5. **USER_ID Mapping Validation**
   - All USER_PROFILES.USER_ID mapped to ADMIN.USERS.ID ✓
   - Note: Training data uses placeholder IDs (TRAIN_1, etc.) - expected

## Validation Results

```
✓ ALL VALIDATIONS PASSED

Row Counts: ✓ PASS
Data Types: ✓ PASS
Constraints: ✓ PASS
Data Quality: ✓ PASS
User Id Mapping: ✓ PASS
```

## Key Metrics

- **Training Data**: 45,858 rows, 28.87% churn rate
- **User Profiles**: 4,142 rows, 28.9% churn rate
- **Data Quality**: All constraints enforced, ranges valid
- **Mapping**: All USER_IDs properly mapped

## Usage

```bash
python scripts/validate_churn_data.py
```

## Next Steps

1. ✅ **Task 2.6 Complete**: Data validation passed
2. ⏳ **Task 2.7**: Create feature engineering views in OML schema
3. ⏳ **Task 2.8**: Validate dataset produces reasonable model performance (AUC > 0.70)

## Notes

- Minor warning: 100 USER_IDs not in UUID format (expected - these are placeholder IDs in training data)
- All critical validations passed
- Data is ready for feature engineering and model training
