# OML Notebooks Execution Guide

## Quick Start

1. **Import Notebooks**: 
   - For OML Notebooks UI: Copy cells from markdown files or import JSON
   - Each cell should be created as a new paragraph in OML Notebooks

2. **Execution Order**: Run cells sequentially from top to bottom

3. **Prerequisites**: Ensure all database objects exist before running

## Original Model Workflow

### Step 1: Create Database Views
- **Cell Type**: SQL (`%script`)
- **Purpose**: Create `CHURN_FEATURES` and `CHURN_TRAINING_DATA` views
- **Expected Output**: Views created successfully

### Step 2: Check OML4Py Connection
- **Cell Type**: Python (`%python`)
- **Purpose**: Verify OML connection
- **Expected Output**: `OML Connected: True`

### Step 3: Explore Data
- **Cell Type**: Python (`%python`)
- **Purpose**: Load and explore feature data
- **Expected Output**: Data shape and segment distribution

### Step 4: Prepare Features and Split Data
- **Cell Type**: Python (`%python`)
- **Purpose**: Prepare training/test split
- **Expected Output**: Train/test sizes and churn rates

### Step 5: Train XGBoost Model
- **Cell Type**: Python (`%python`)
- **Purpose**: Train baseline model
- **Expected Output**: Training completed message

### Step 6: Evaluate Model
- **Cell Type**: Python (`%python`)
- **Purpose**: Calculate performance metrics
- **Expected Output**: Accuracy, Precision, Recall, F1, AUC-ROC

### Step 7: Feature Importance
- **Cell Type**: Python (`%python`)
- **Purpose**: Analyze feature importance
- **Expected Output**: Top 20 features with importance scores

### Step 8: Save Model
- **Cell Type**: Python (`%python`)
- **Purpose**: Persist model to OML datastore
- **Expected Output**: Model saved confirmation

### Step 9: Optimize Threshold
- **Cell Type**: Python (`%python`)
- **Purpose**: Find optimal probability threshold
- **Expected Output**: Optimal threshold value (typically 0.1)

### Step 10: Score All Customers
- **Cell Type**: Python (`%python`)
- **Purpose**: Generate churn risk scores for all customers
- **Expected Output**: At-risk customer count and LTV at risk

### Step 11: Cohort-Level Metrics
- **Cell Type**: Python (`%python`)
- **Purpose**: Analyze risk by customer segment
- **Expected Output**: Cohort metrics table

### Step 12: Analyze Risk Factors
- **Cell Type**: Python (`%python`)
- **Purpose**: Identify top risk factors
- **Expected Output**: Risk factors table

### Step 13: Summary Report
- **Cell Type**: Python (`%python`)
- **Purpose**: Generate comprehensive summary
- **Expected Output**: Complete model development summary

## Enhanced Model Workflow

### Step 1: Create Enhanced Features View
- **Cell Type**: SQL (`%script`)
- **Purpose**: Create view with 17 new engineered features
- **Expected Output**: View created with new features

### Step 2: Create Enhanced Training Data View
- **Cell Type**: SQL (`%script`)
- **Purpose**: Create training data view with enhanced features
- **Expected Output**: View created

### Step 3: Verify Enhanced Views
- **Cell Type**: SQL (`%script`)
- **Purpose**: Verify new features exist
- **Expected Output**: List of new feature columns

### Step 4: Prepare Features and Split Data
- **Cell Type**: Python (`%python`)
- **Purpose**: Convert categorical features and split data
- **Expected Output**: Train/test split with categorical features encoded

### Step 5: Train Enhanced Model
- **Cell Type**: Python (`%python`)
- **Purpose**: Train model with enhanced features
- **Expected Output**: Training completed

### Step 6: Evaluate Enhanced Model
- **Cell Type**: Python (`%python`)
- **Purpose**: Evaluate and compare with original
- **Expected Output**: Metrics and comparison table

### Step 7: Feature Importance
- **Cell Type**: Python (`%python`)
- **Purpose**: Analyze enhanced model feature importance
- **Expected Output**: Top features including new engineered ones

### Step 8: Summary
- **Cell Type**: Python (`%python`)
- **Purpose**: Summary and recommendations
- **Expected Output**: Feature engineering summary

## Common Issues and Solutions

### Issue: "View does not exist"
**Solution**: Run Step 1 SQL cells first to create views

### Issue: "OML not connected"
**Solution**: Check database connection and OML service status

### Issue: "Invalid training data"
**Solution**: 
- Check for NULL or infinity values
- Ensure all features are numeric
- Verify data types match

### Issue: "KeyError: column not found"
**Solution**: 
- Verify column names match exactly
- Check if categorical columns need conversion
- Ensure feature list matches training data

### Issue: "Model performance is poor"
**Solution**: 
- Try enhanced model with feature engineering
- Consider hyperparameter tuning
- Review churn definition
- Check data quality

## Best Practices

1. **Run Original Model First**: Establish baseline before enhancements
2. **Save Models**: Use Step 8 to persist models for later use
3. **Document Results**: Keep track of performance metrics
4. **Iterate**: Use comparison results to guide next improvements
5. **Validate**: Test on holdout data before production deployment

## Notes

- **Categorical Features**: Enhanced model includes categorical features converted to numeric
- **Threshold**: Both models use optimized threshold (0.1) instead of default 0.5
- **Feature Engineering**: Enhanced model adds 17 new features
- **Model Comparison**: Enhanced workflow compares with original model automatically
