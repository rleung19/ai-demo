# Sampling Strategy Comparison Results

## Analysis Results

### Churn Rate Comparison

| Strategy | Churn Rate | Difference from Full Dataset |
|----------|------------|------------------------------|
| **Full Dataset** | 28.90% | - |
| **Sequential** | 29.24% | +0.34% ⚠️ |
| **Random** | 28.95% | +0.05% ✅ |
| **Stratified** | 28.90% | 0.00% ✅ **BEST** |

### Feature Distribution Comparison

All strategies are very close to the full dataset:

| Feature | Full Dataset | Sequential | Random | Stratified |
|---------|--------------|------------|--------|------------|
| Age | 37.79 | 37.89 (0.3% diff) | 37.79 (0.0% diff) | 37.81 (0.0% diff) |
| Total_Purchases | 13.12 | 13.07 (0.4% diff) | 13.19 (0.6% diff) | 13.10 (0.1% diff) |
| Average_Order_Value | 119.45 | 119.72 (0.2% diff) | 120.74 (1.1% diff) | 118.95 (0.4% diff) |
| Days_Since_Last_Purchase | 29.27 | 28.91 (1.2% diff) | 28.61 (2.2% diff) | 29.51 (0.9% diff) |

## Key Findings

### Sequential Strategy Issues

1. **Small bias**: Churn rate is 0.34% higher (29.24% vs 28.90%)
2. **May indicate sorting**: First rows might be slightly different
3. **Not ideal**: Could affect model training

### Random Strategy

1. **Very close**: Churn rate within 0.05% of full dataset
2. **Representative**: Good feature distributions
3. **Good choice**: If you don't need exact churn rate

### Stratified Strategy ⭐ BEST

1. **Perfect match**: Maintains exact 28.90% churn rate
2. **Representative**: Feature distributions match full dataset
3. **Best for training**: Ensures class balance
4. **Recommended**: Use this for model training

## Recommendation

### Use Stratified Sampling ✅

**Why**:
- ✅ Maintains exact churn rate (28.90%)
- ✅ Representative feature distributions
- ✅ Best for model training (proper class balance)
- ✅ No bias from data ordering

**Action Taken**:
- Updated mapping script to support 'stratified' strategy
- Re-mapped dataset using stratified sampling
- Dataset now has exact churn rate match

## Updated Dataset

The mapped dataset now uses **stratified sampling**:
- 4,142 rows (one per user)
- Churn rate: 28.90% (exact match)
- Representative of full dataset
- Ready for model training
