# Download and Examine dhairyajeetsingh Dataset

## Step 1: Download the Dataset

### Option A: Using Kaggle API (Automated)

1. **Install Kaggle package**:
   ```bash
   pip install kaggle
   ```

2. **Set up Kaggle API credentials**:
   - Go to https://www.kaggle.com/settings
   - Click "Create New Token" (downloads `kaggle.json`)
   - Place `kaggle.json` in `~/.kaggle/`:
     ```bash
     mkdir -p ~/.kaggle
     mv ~/Downloads/kaggle.json ~/.kaggle/
     chmod 600 ~/.kaggle/kaggle.json
     ```

3. **Run download script**:
   ```bash
   python scripts/download_kaggle_dataset.py
   ```

### Option B: Manual Download

1. **Go to Kaggle**:
   - Visit: https://www.kaggle.com/datasets
   - Search for: `"dhairyajeetsingh" "ecommerce customer behavior"`

2. **Download the dataset**:
   - Click on the dataset
   - Click "Download" button
   - Extract the ZIP file

3. **Save to project**:
   ```bash
   mkdir -p data/raw
   # Move CSV file(s) to data/raw/
   mv ~/Downloads/ecommerce_customer_behavior*.csv data/raw/
   ```

## Step 2: Examine the Dataset

Once downloaded, examine the dataset structure:

```bash
# Find the CSV file
ls -lh data/raw/*.csv

# Examine the dataset
python scripts/examine_dataset.py data/raw/<filename>.csv
```

The examination script will show:
- Dataset size (rows × columns)
- Column names and types
- Missing values
- Churn label (if exists)
- Data quality metrics
- Sample data
- Ecommerce-relevant features

## Step 3: Verify Key Requirements

After examination, verify:

- [ ] **Churn label exists** (or can be derived)
- [ ] **~50,000 rows** (or close)
- [ ] **~25 features** (or close)
- [ ] **Low missing values** (<5%)
- [ ] **Ecommerce features** present (orders, payments, devices, etc.)

## Step 4: Next Steps

If dataset looks good:
1. Proceed to **Section 2.2** (Evaluate dataset quality)
2. Then **Section 2.3** (Download and prepare dataset locally)
3. Then **Section 2.4** (Create data mapping document)

If dataset doesn't meet requirements:
- Consider **samuelsemaya** as backup
- Or search for alternative datasets

## Troubleshooting

**If Kaggle API doesn't work**:
- Use manual download (Option B)
- Or check Kaggle API credentials

**If dataset not found**:
- Search Kaggle with different keywords
- Check if dataset name has changed
- Look for similar datasets

**If examination script fails**:
- Check if pandas is installed: `pip install pandas`
- Verify CSV file is valid
- Check file path is correct
