# Local Model Comparison Results

## Test Date
2026-01-18

## Models Tested

### Successful Models

1. **XGBoost** 🏆
   - **AUC**: 0.9269 (92.69%)
   - **Accuracy**: 92.17%
   - **Precision**: 92.81%
   - **Recall**: 79.00%
   - **F1 Score**: 0.8535
   - **Status**: ✅ **BEST MODEL**

2. **CatBoost**
   - **AUC**: 0.9255 (92.55%)
   - **Accuracy**: 92.00%
   - **Precision**: 92.91%
   - **Recall**: 78.25%
   - **F1 Score**: 0.8495
   - **Status**: ✅ Excellent performance

3. **LightGBM**
   - **AUC**: 0.9251 (92.51%)
   - **Accuracy**: 92.00%
   - **Precision**: 92.16%
   - **Recall**: 79.00%
   - **F1 Score**: 0.8508
   - **Status**: ✅ Excellent performance

4. **GradientBoosting**
   - **AUC**: 0.9247 (92.47%)
   - **Accuracy**: 92.01%
   - **Precision**: 92.12%
   - **Recall**: 79.08%
   - **F1 Score**: 0.8510
   - **Status**: ✅ Excellent performance

5. **RandomForest**
   - **AUC**: 0.9199 (91.99%)
   - **Accuracy**: 90.98%
   - **Precision**: 92.65%
   - **Recall**: 74.70%
   - **F1 Score**: 0.8271
   - **Status**: ✅ Excellent performance

6. **AdaBoost**
   - **AUC**: 0.9192 (91.92%)
   - **Accuracy**: 90.45%
   - **Precision**: 93.43%
   - **Recall**: 71.98%
   - **F1 Score**: 0.8131
   - **Status**: ✅ Good performance

4. **LightGBM**
   - **Status**: ⚠️ Not installed
   - **Fix**: `pip install lightgbm`
   - **Note**: Optional, fast gradient boosting

5. **CatBoost**
   - **Status**: ⚠️ Not installed
   - **Fix**: `pip install catboost`
   - **Note**: Optional, good for categorical features

6. **AdaBoost**
   - **Status**: ❌ Failed - API change
   - **Error**: `base_estimator` deprecated, should use `estimator`
   - **Fix**: Updated in script

## Performance Summary

| Model | AUC | Status | Recommendation |
|-------|-----|--------|----------------|
| **XGBoost** | **0.9269** | 🏆 **Best** | **Use for production** |
| CatBoost | 0.9255 | ✅ Excellent | Excellent alternative |
| LightGBM | 0.9251 | ✅ Excellent | Excellent alternative |
| GradientBoosting | 0.9247 | ✅ Excellent | Good alternative |
| RandomForest | 0.9199 | ✅ Excellent | Good alternative |
| AdaBoost | 0.9192 | ✅ Good | Acceptable alternative |

## Key Findings

1. **GradientBoosting is the best model** with AUC 0.9247
2. **RandomForest is a close second** with AUC 0.9199
3. **Both models significantly outperform OML4Py** (AUC ~0.50)
4. **Local training with proper hyperparameters is essential** for good performance

## Comparison with OML4Py

| Metric | Local XGBoost | OML4Py RandomForest |
|--------|--------------|---------------------|
| AUC | **0.9269** | 0.4986 |
| Accuracy | **92.17%** | 59.91% |
| Precision | **92.81%** | 27.36% |
| Recall | **79.00%** | 23.49% |
| F1 Score | **0.8535** | 0.2528 |

**Conclusion**: Local training achieves **86% better performance** than OML4Py.

## Recommendations

1. **Use XGBoost for production** 🏆
   - Best overall performance (AUC 0.9269)
   - Excellent balance of precision and recall
   - Highest F1 score (0.8535)

2. **CatBoost as backup**
   - Very close performance (AUC 0.9255)
   - Slightly better precision (92.91%)
   - Good alternative if XGBoost has issues

3. **Install XGBoost** (optional)
   - Install OpenMP: `brew install libomp`
   - Re-run comparison to test XGBoost
   - May achieve similar or better performance

4. **Deploy locally trained model**
   - Save the GradientBoosting model
   - Use for batch scoring
   - Consider deploying to OML Datastore if needed

## Next Steps

1. ✅ **Model Selected**: XGBoost (AUC 0.9269)
2. ✅ **Save Model**: Script created to save best model
3. ⏳ **Scoring Script**: Update to use XGBoost for batch scoring
4. ⏳ **Deploy**: Deploy model for production use

## Related Documentation

- `docs/LOCAL_MODEL_COMPARISON_GUIDE.md` - How to run the comparison
- `scripts/train_models_local_comparison.py` - Comparison script
- `docs/OML4PY_FINAL_ANALYSIS.md` - OML4Py limitations
