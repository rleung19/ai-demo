# Dataset Research: Churn Prediction for Fashion Ecommerce

## Requirements

- **Industry**: Online ecommerce/retail (fashion, cosmetics, accessories)
- **Similar to**: Net-a-Porter, ASOS
- **Must have**: Proven churn prediction performance (AUC > 0.70)
- **Must be**: Online ecommerce or retailer dataset

## Top Candidate Datasets

### 1. **Ecommerce Customer Behavior Dataset** by dhairyajeetsingh ⭐ RECOMMENDED

**Kaggle Link**: [Search for "dhairyajeetsingh ecommerce customer behavior"](https://www.kaggle.com/datasets)

**Details**:
- **Size**: ~50,000 rows, ~25 features
- **Industry**: Ecommerce/Online Retail
- **Features**: Customer behavior, purchase history, spending patterns, demographics
- **Churn Label**: Likely included or derivable

**Pros**:
- ✅ Directly ecommerce-focused (not telco/banking)
- ✅ Good size for training (50k rows)
- ✅ Rich feature set (~25 features)
- ✅ Behavioral data (purchases, spending, engagement)
- ✅ Suitable for fashion/retail use case

**Cons**:
- ⚠️ May not have product category details (fashion vs other)
- ⚠️ Need to verify churn label exists

**Why it fits**:
- Ecommerce context matches your use case
- Behavioral features (purchase frequency, recency, spending) are key for fashion retail
- Can map to your existing USER_ID structure

---

### 2. **Online Retail II Dataset** (UCI Machine Learning Repository)

**Source**: UCI ML Repository / Kaggle

**Details**:
- **Size**: ~500,000+ transactions (UK online retail, 2009-2011)
- **Industry**: Online retail (real UK ecommerce company)
- **Features**: Invoice data, product descriptions, quantities, prices, customer IDs
- **Churn Label**: Not included - need to derive (e.g., no purchase in 90 days)

**Pros**:
- ✅ Real retail transaction data
- ✅ Large dataset (good for robust models)
- ✅ Product-level detail (can identify fashion/accessories)
- ✅ Time-series data (can build RFM features)
- ✅ Real customer behavior patterns

**Cons**:
- ⚠️ Older data (2009-2011) - patterns may differ
- ⚠️ No pre-defined churn label
- ⚠️ UK-based (may have regional differences)
- ⚠️ Need to engineer churn definition

**Why it fits**:
- Real retail transactions
- Can filter for fashion/accessories products
- Rich enough for feature engineering (RFM analysis)

---

### 3. **Customer Churn Dataset** by muhammadshahidazeem

**Details**:
- **Size**: ~440,833 training rows, 12 features
- **Industry**: Subscription-based (mixed)
- **Features**: Age, gender, tenure, usage frequency, support calls, subscription type, contract length

**Pros**:
- ✅ Very large dataset (good statistical power)
- ✅ Proven for churn prediction
- ✅ Good feature variety

**Cons**:
- ❌ Subscription-based (not purchase-based ecommerce)
- ❌ Less relevant for fashion retail
- ❌ May lack product/category features

**Verdict**: Not ideal for fashion ecommerce use case

---

### 4. **Telco Customer Churn** (IBM Sample Dataset)

**Details**:
- **Size**: ~7,000 rows, 20-21 features
- **Industry**: Telecommunications
- **Features**: Contract type, tenure, monthly charges, services

**Pros**:
- ✅ Well-documented and understood
- ✅ Good baseline for learning

**Cons**:
- ❌ Telecom industry (not retail/ecommerce)
- ❌ Subscription model (not purchase-based)
- ❌ Small dataset

**Verdict**: Not suitable for fashion ecommerce

---

## Recommendation: Hybrid Approach

### Primary Choice: **Ecommerce Customer Behavior Dataset** (dhairyajeetsingh)

**Why**:
1. ✅ Directly ecommerce-focused
2. ✅ Good size (50k rows)
3. ✅ Rich behavioral features
4. ✅ Likely has churn labels
5. ✅ Can map to your USER_ID structure

### Secondary/Backup: **Online Retail II Dataset**

**Why**:
1. ✅ Real retail transaction data
2. ✅ Large dataset (500k+ transactions)
3. ✅ Can filter for fashion products
4. ✅ Rich for feature engineering

**Use if**: Primary dataset doesn't have churn labels or needs more data

---

## Next Steps

1. **Download and examine** "Ecommerce Customer Behavior Dataset"
   - Check if churn label exists
   - Review feature list
   - Verify data quality

2. **If primary doesn't work**, try "Online Retail II"
   - Derive churn definition (e.g., 90-day inactivity)
   - Engineer RFM features
   - Filter for fashion/accessories products

3. **Map to your USER_ID structure**
   - Match dataset rows to ADMIN.USERS.ID
   - Preserve existing user relationships

---

## Evaluation Criteria

When evaluating datasets, check:

- [ ] **Churn label exists** or easily derivable
- [ ] **Ecommerce/retail context** (not telco/banking)
- [ ] **Behavioral features** (purchases, frequency, recency, spending)
- [ ] **Size** (at least 10k+ rows, ideally 50k+)
- [ ] **Feature richness** (15+ features for good model)
- [ ] **Data quality** (no major missing values, realistic distributions)

---

## Action Items

1. Search Kaggle for "dhairyajeetsingh ecommerce customer behavior"
2. Download and examine the dataset
3. Check feature list and churn label
4. If suitable, proceed with mapping to USER_ID
5. If not, evaluate "Online Retail II" as backup
