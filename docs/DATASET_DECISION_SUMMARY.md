# Dataset Decision Summary

## Final Recommendation: **dhairyajeetsingh** ⭐

### Why This is the Best Choice

| Factor | dhairyajeetsingh | samuelsemaya | Winner |
|--------|------------------|--------------|--------|
| **Performance** | 91% acc, F1=0.83 | 92% acc, F1=0.78 | 🥇 Tie (both excellent) |
| **Cleaning Effort** | ⭐ **LOW** (synthetic) | ⚠️ **MODERATE-HIGH** (real) | 🥇 dhairyajeetsingh |
| **Dataset Size** | 50,000 rows | 3,270 rows | 🥇 dhairyajeetsingh |
| **Features** | ~25 features | 10 features | 🥇 dhairyajeetsingh |
| **Precision** | 0.92 | 0.70 | 🥇 dhairyajeetsingh |
| **Overall** | **6 wins** | 1 win | 🥇 **dhairyajeetsingh** |

---

## Key Insights

### dhairyajeetsingh Advantages:
1. ✅ **Less cleaning work** - Synthetic data is cleaner by design
2. ✅ **Larger dataset** - 50k rows = more robust models
3. ✅ **More features** - 25 features = better feature engineering
4. ✅ **Better precision** - 0.92 = fewer false positives (important!)
5. ✅ **Proven performance** - 91% accuracy, F1=0.83
6. ✅ **More generic** - Easier to adapt to your use case

### samuelsemaya Advantages:
1. ✅ **Real data** - Authentic patterns
2. ✅ **Higher recall** - 0.89 = catches more churners
3. ✅ **Churn label confirmed** - Already verified

### Trade-offs:

**dhairyajeetsingh**:
- ⚠️ Synthetic (not real) - but patterns are realistic
- ⚠️ Lower recall (0.76) - might miss ~24% of churners
- ⚠️ Need to verify churn label

**samuelsemaya**:
- ⚠️ More cleaning work required
- ⚠️ Smaller dataset (3k vs 50k)
- ⚠️ Fewer features (10 vs 25)
- ⚠️ Lower precision (0.70) - more false positives

---

## Decision Rationale

**For a demo/workshop context**, **dhairyajeetsingh is better** because:

1. **Faster setup** - Less cleaning = faster to get started
2. **More robust** - Larger dataset = better generalization
3. **Better precision** - Fewer false alarms = better business decisions
4. **More features** - Better for demonstrating feature engineering
5. **Proven performance** - 91% accuracy meets your requirements

**The only downside** is it's synthetic, but for a demo this is actually an advantage (cleaner, faster setup).

---

## Action Plan

1. **Download dhairyajeetsingh dataset**
2. **Quick check**: Verify churn label exists (if not, derive it)
3. **Minimal cleaning**: Synthetic data should be clean
4. **Map to USER_ID**: Match to your existing users
5. **Train model**: Target 91% accuracy, F1=0.83

**If churn label is missing**: Use samuelsemaya as backup (but expect more cleaning work).
