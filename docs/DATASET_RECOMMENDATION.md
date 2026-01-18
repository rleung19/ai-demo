# Dataset Recommendation: Fashion Ecommerce Churn Prediction

## Your Requirements
- ✅ Online ecommerce/retail industry (fashion, cosmetics, accessories)
- ✅ Similar to Net-a-Porter / ASOS
- ✅ Proven churn prediction performance (AUC > 0.70)
- ✅ Must map to existing USER_ID in ADMIN schema

## Top 3 Recommendations

### 🥇 **#1 RECOMMENDED: Ecommerce Customer Behavior Dataset** by dhairyajeetsingh

**Kaggle Search**: Search for `"dhairyajeetsingh" "ecommerce customer behavior"`

**Details**:
- **Size**: ~50,000 rows, ~25 features
- **Industry**: Ecommerce/Online Retail ✅
- **Features**: Customer behavior, purchase history, spending, demographics, engagement
- **Churn Label**: Need to verify (may need to derive)

**Why This is Best**:
- ✅ **Directly ecommerce-focused** (not telco/banking/subscription)
- ✅ **Good size** (50k rows = robust model training)
- ✅ **Rich feature set** (~25 features including behavioral metrics)
- ✅ **Behavioral data** (purchases, frequency, recency, spending) - perfect for fashion retail
- ✅ **Recent dataset** (likely has modern ecommerce features)

**What to Check**:
- [ ] Does it have a churn label column?
- [ ] What are the exact feature names?
- [ ] Are there product category features?
- [ ] Data quality (missing values, distributions)

**Next Steps**:
1. Search Kaggle: `dhairyajeetsingh ecommerce customer behavior`
2. Download and examine the dataset
3. Review feature list
4. Check for churn label or derive one (e.g., 90-day inactivity)

---

### 🥈 **#2 BACKUP: E-commerce Customer Churn Analysis & Prediction** by Ankit Verma

**Kaggle Search**: Search for `"Ankit Verma" "ecommerce customer churn"`

**Details**:
- **Size**: ~5,630+ customers, ~20 features
- **Industry**: Ecommerce ✅
- **Features**: User basics, purchase history, behavior/service usage
- **Churn Label**: ✅ **Included** (makes it easier!)

**Why This Works**:
- ✅ **Has churn label** (no need to derive)
- ✅ **Ecommerce context**
- ✅ **Good for prototyping** (smaller size)
- ✅ **Behavioral features** included

**Trade-offs**:
- ⚠️ Smaller dataset (may need data augmentation)
- ⚠️ Need to verify feature richness

**Use if**: Primary dataset doesn't have churn labels

---

### 🥉 **#3 ALTERNATIVE: Online Retail II Dataset** (UCI/Kaggle)

**Kaggle Search**: Search for `"online retail" "UK" "transaction"`

**Details**:
- **Size**: ~500,000+ transactions (UK online retail, 2009-2011)
- **Industry**: Real UK online retail ✅
- **Features**: Invoice data, products, quantities, prices, customer IDs, timestamps
- **Churn Label**: ❌ Need to derive (e.g., no purchase in 90 days)

**Why This Works**:
- ✅ **Real retail transaction data** (authentic patterns)
- ✅ **Very large dataset** (500k+ transactions = robust models)
- ✅ **Product-level detail** (can filter for fashion/accessories)
- ✅ **Time-series data** (perfect for RFM analysis)
- ✅ **Rich for feature engineering**

**Trade-offs**:
- ⚠️ **Older data** (2009-2011) - patterns may differ from 2026
- ⚠️ **No churn label** - need to define (e.g., 90-day inactivity)
- ⚠️ **UK-based** - may have regional differences
- ⚠️ **More preprocessing** required

**Use if**: Need more data or want real transaction patterns

---

## Final Recommendation: Start with #1

### Action Plan

1. **Download Primary Dataset** (#1: dhairyajeetsingh)
   ```bash
   # Search Kaggle and download
   # Expected filename: ecommerce_customer_behavior_dataset.csv
   ```

2. **Examine the Dataset**
   - Check if churn label exists
   - Review all feature columns
   - Check data quality (missing values, distributions)
   - Verify it's truly ecommerce (not subscription)

3. **If Primary Works**:
   - Map to your USER_ID structure
   - Load into OML schema
   - Proceed with model training

4. **If Primary Doesn't Work**:
   - Try #2 (Ankit Verma - has churn label)
   - Or #3 (Online Retail II - real transactions)

---

## Mapping Strategy to Your USER_ID

Once you have the dataset, map it to your existing `ADMIN.USERS.ID`:

```sql
-- Strategy: Match dataset rows to existing users
-- Option 1: Sequential mapping (if dataset has same number of rows)
-- Option 2: Random sampling (if dataset is larger)
-- Option 3: Feature-based matching (if demographics match)

-- Example mapping:
CREATE TABLE OML.CHURN_DATASET AS
SELECT 
    u.ID AS USER_ID,  -- Your existing ADMIN.USERS.ID
    k.*                -- All features from Kaggle dataset
FROM (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY customer_id) AS rn,
        *
    FROM kaggle_dataset
) k
JOIN (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY ID) AS rn,
        ID
    FROM ADMIN.USERS
    WHERE IS_ACTIVE = 1
) u ON k.rn = u.rn;
```

---

## Evaluation Checklist

Before finalizing a dataset, verify:

- [ ] **Ecommerce/retail context** (not telco/banking/subscription)
- [ ] **Churn label exists** or easily derivable
- [ ] **Behavioral features** (purchases, frequency, recency, spending)
- [ ] **Size** (at least 10k+ rows, ideally 50k+)
- [ ] **Feature richness** (15+ features)
- [ ] **Data quality** (no major missing values, realistic distributions)
- [ ] **Can map to USER_ID** (same or more rows than your users)

---

## Next Steps

1. **Search Kaggle** for "dhairyajeetsingh ecommerce customer behavior"
2. **Download** the dataset
3. **Examine** features and churn label
4. **If suitable**, proceed to Section 2.4 (data mapping)
5. **If not**, evaluate backup options (#2 or #3)

---

## Resources

- **Kaggle Search**: https://www.kaggle.com/datasets
- **Search Terms**: 
  - "ecommerce customer churn"
  - "online retail churn"
  - "customer behavior dataset"
  - "dhairyajeetsingh"
  - "Ankit Verma ecommerce"
