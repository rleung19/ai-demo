# Local Model Training and Comparison Guide

## Purpose

This script trains multiple machine learning models locally with proper hyperparameters and compares their performance. This helps identify the best model for your churn prediction task.

## Why Local Training?

- **OML4Py Limitations**: OML4Py doesn't support hyperparameters, resulting in poor performance (AUC ~0.50)
- **Better Performance**: Local training with proper hyperparameters achieves AUC ~0.90+
- **Model Comparison**: Test multiple algorithms to find the best one
- **Hyperparameter Control**: Full control over model parameters

## Models Tested

1. **RandomForest** - Ensemble of decision trees
2. **XGBoost** - Gradient boosting with regularization
3. **GradientBoosting** - Sklearn's gradient boosting
4. **LightGBM** - Fast gradient boosting (if installed)
5. **CatBoost** - Categorical boosting (if installed)
6. **AdaBoost** - Adaptive boosting

## Usage

### Basic Usage

```bash
python scripts/train_models_local_comparison.py
```

### Prerequisites

**Required**:
- `scikit-learn` - Core ML library
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `oracledb` - Database connection
- `python-dotenv` - Environment variables

**Optional** (for additional models):
- `xgboost` - XGBoost algorithm
- `lightgbm` - LightGBM algorithm (install with: `pip install lightgbm`)
- `catboost` - CatBoost algorithm (install with: `pip install catboost`)

### Install Optional Dependencies

```bash
# Install all optional models
pip install xgboost lightgbm catboost
```

## What It Does

1. **Loads Data**: From `OML.CHURN_TRAINING_DATA` view
2. **Cleans Data**: Handles NaN, infinity, type conversion
3. **Splits Data**: 80% training, 20% validation (stratified)
4. **Trains Models**: Multiple algorithms with proper hyperparameters
5. **Compares Performance**: AUC, Accuracy, Precision, Recall, F1
6. **Recommends Best**: Identifies top-performing model

## Output

The script displays:

1. **Data Loading Summary**:
   - Number of rows and features
   - Churn rate
   - Train/validation split

2. **Training Progress**:
   - Each model's training status
   - Warnings for unavailable models

3. **Performance Comparison Table**:
   ```
   Model              AUC        Accuracy    Precision   Recall      F1
   --------------------------------------------------------------------
   RandomForest       0.9190     0.9106      0.9255      0.7508      0.8290
   XGBoost            0.9150     0.9050      0.9200      0.7400      0.8200
   ...
   ```

4. **Best Model Recommendation**:
   - Model name
   - All performance metrics
   - Performance assessment (excellent/good/acceptable/poor)

## Expected Results

Based on Task 2.8 validation:
- **RandomForest**: AUC ~0.9190 (excellent)
- **XGBoost**: AUC ~0.90+ (excellent)
- **Other models**: Varies, but should be >0.70

## Next Steps

After identifying the best model:

1. **Save the Model**: Use the best model for production
2. **Deploy to OML**: If needed, save model and deploy to OML Datastore
3. **Create Scoring Script**: Use the best model for batch scoring
4. **Update Notebook**: Use the best model's hyperparameters in OML notebook (if OML supports them)

## Troubleshooting

### Error: XGBoost not available
- **Solution**: Install with `pip install xgboost`
- **Note**: XGBoost requires OpenMP on macOS (`brew install libomp`)

### Error: LightGBM/CatBoost not available
- **Solution**: Install with `pip install lightgbm` or `pip install catboost`
- **Note**: These are optional - script will continue without them

### Error: Database connection failed
- **Solution**: Check `.env` file configuration
- Verify ADB instance is running
- Test connection with `scripts/test-python-connection.py`

### Poor Performance (AUC < 0.70)
- Check data quality
- Verify features are informative
- Review data cleaning steps
- Check for data leakage

## Comparison with OML4Py

| Aspect | Local Training | OML4Py |
|--------|---------------|--------|
| **Hyperparameters** | ✅ Full control | ❌ Not supported |
| **Performance** | ✅ AUC ~0.90+ | ❌ AUC ~0.50 |
| **Model Selection** | ✅ Multiple models | ⚠️ Limited |
| **Training Location** | Local machine | In-database |
| **Data Movement** | Pulls to local | Stays in DB |

## Related Documentation

- `docs/TASK_2.8_GUIDE.md` - Initial validation (AUC 0.9190)
- `docs/OML4PY_FINAL_ANALYSIS.md` - OML4Py limitations
- `scripts/validate_model_performance.py` - Single model validation
