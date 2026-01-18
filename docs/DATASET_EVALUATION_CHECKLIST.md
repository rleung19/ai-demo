# Dataset Evaluation Checklist

Use this checklist to evaluate each dataset and compare them.

## For Each Dataset, Check:

### Basic Information
- [ ] **Dataset Name**: ________________
- [ ] **Kaggle Link**: ________________
- [ ] **Author/Creator**: ________________
- [ ] **Dataset Type**: Dataset / Notebook / Competition

### Size & Scale
- [ ] **Number of Rows**: ________________
- [ ] **Number of Columns/Features**: ________________
- [ ] **File Size**: ________________
- [ ] **Training/Test Split**: ________________ (if applicable)

### Features (List All Columns)
- [ ] **Demographic Features**: ________________
- [ ] **Behavioral Features**: ________________
- [ ] **Transactional Features**: ________________
- [ ] **Engagement Features**: ________________
- [ ] **Other Features**: ________________

### Churn Label
- [ ] **Churn Label Exists**: Yes / No
- [ ] **Churn Column Name**: ________________
- [ ] **Churn Definition**: ________________
- [ ] **Churn Rate**: ________________ (%)
- [ ] **Class Balance**: Balanced / Imbalanced

### Data Quality
- [ ] **Missing Values**: None / Some / Many
- [ ] **Data Types**: Appropriate / Need conversion
- [ ] **Outliers**: None / Some / Many
- [ ] **Data Quality**: Good / Fair / Poor

### Industry Match
- [ ] **Industry**: Ecommerce / Retail / Other: ________________
- [ ] **Matches Fashion Ecommerce**: Yes / No / Partial
- [ ] **Similar to Net-a-Porter/ASOS**: Yes / No / Partial

### Documentation
- [ ] **Description Available**: Yes / No
- [ ] **Column Descriptions**: Yes / No
- [ ] **Usage Examples**: Yes / No
- [ ] **Performance Metrics**: Yes / No (AUC, accuracy, etc.)

### Proven Performance
- [ ] **Model Performance Mentioned**: Yes / No
- [ ] **AUC Score**: ________________ (if mentioned)
- [ ] **Other Metrics**: ________________
- [ ] **Notebooks/Examples**: ________________ (number)

---

## Comparison Matrix

Fill this out for each dataset:

| Criterion | My #1 (dhairyajeetsingh) | Your #1 (samuelsemaya) | Your #2 (hassaneskikri) | Winner |
|-----------|--------------------------|------------------------|-------------------------|--------|
| **Size (rows)** | ~50,000 | ? | ? | ? |
| **Features (cols)** | ~25 | ? | ? | ? |
| **Churn Label** | ? | ? | ? | ? |
| **Ecommerce Match** | ✅ | ✅ | ✅ | Tie |
| **Data Quality** | ? | ? | ? | ? |
| **Documentation** | ? | ? | ? | ? |
| **Proven Performance** | ? | ? | ? | ? |
| **Ease of Use** | ? | ? | ? | ? |

---

## How to Evaluate Your Datasets

### For samuelsemaya (Notebook):
1. Open the notebook link
2. Check the **"Data"** section - what dataset does it use?
3. Look for **dataset references** or **data loading code**
4. Note the **churn definition** used in the analysis
5. Check if there's a **dataset link** in the notebook
6. Review the **feature engineering** - what features are created?
7. Note any **performance metrics** (AUC, accuracy, etc.)

### For hassaneskikri (Dataset):
1. Open the dataset link
2. Go to **"Data"** tab
3. Check **file details**:
   - File name(s)
   - File size
   - Number of rows (if shown)
4. Review **column descriptions** (if available)
5. Check **data preview** (first few rows)
6. Look for **"Discussion"** or **"Notebooks"** tabs for usage examples
7. Note if **churn label** exists in the columns

---

## Decision Criteria

**Choose the dataset that scores highest on**:

1. ✅ **Has churn label** (critical - saves time)
2. ✅ **Good size** (10k+ rows, ideally 50k+)
3. ✅ **Rich features** (15+ features)
4. ✅ **Ecommerce context** (not telco/banking)
5. ✅ **Good documentation** (understandable)
6. ✅ **Proven performance** (AUC > 0.70 mentioned)

---

## Next Steps

1. **Fill out the checklist** for all three datasets
2. **Compare scores** using the comparison matrix
3. **Choose the winner** based on criteria
4. **Download and examine** the chosen dataset
5. **Proceed to Section 2.2-2.3** (evaluate and prepare)

---

## Quick Tips

- **If samuelsemaya is just a notebook**: Find the dataset it uses and evaluate that
- **If hassaneskikri is based on Online Retail II**: It's likely good but may need churn derivation
- **If both are smaller than 50k**: Consider using the larger one or combining them
- **If churn label is missing**: You can derive it (e.g., 90-day inactivity), but it's more work
