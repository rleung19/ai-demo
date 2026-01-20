# Download dhairyajeetsingh Dataset - Quick Start

## Dataset Information

- **Name**: Ecommerce Customer Behavior Dataset
- **Author**: dhairyajeetsingh
- **Size**: ~50,000 rows, ~25 columns
- **File Size**: ~1.6 MB
- **Kaggle**: Search for `"dhairyajeetsingh" "ecommerce customer behavior"`

## Quick Download Methods

### Method 1: Manual Download (Easiest)

1. **Go to Kaggle**:
   ```
   https://www.kaggle.com/datasets
   ```

2. **Search for**:
   ```
   "dhairyajeetsingh" "ecommerce customer behavior"
   ```

3. **Download**:
   - Click on the dataset
   - Click "Download" button
   - Extract the ZIP file

4. **Save to project**:
   ```bash
   # Create directory if needed
   mkdir -p data/raw
   
   # Move CSV file to data/raw/
   mv ~/Downloads/ecommerce_customer_behavior*.csv data/raw/
   ```

### Method 2: Kaggle API (Automated)

1. **Install Kaggle package**:
   ```bash
   pip install kaggle
   ```

2. **Set up credentials**:
   - Go to https://www.kaggle.com/settings
   - Click "Create New Token"
   - Save `kaggle.json` to `~/.kaggle/`:
     ```bash
     mkdir -p ~/.kaggle
     mv ~/Downloads/kaggle.json ~/.kaggle/
     chmod 600 ~/.kaggle/kaggle.json
     ```

3. **Run download script**:
   ```bash
   python scripts/download_kaggle_dataset.py
   ```

## Examine the Dataset

Once downloaded, run the examination script:

```bash
# Find the CSV file
ls -lh data/raw/*.csv

# Examine the dataset
python scripts/examine_dataset.py data/raw/<filename>.csv
```

## What to Check

The examination script will show:

✅ **Dataset size**: Should be ~50,000 rows, ~25 columns  
✅ **Churn label**: Check if column exists (e.g., "Churn", "churned")  
✅ **Missing values**: Should be low (<5%)  
✅ **Feature types**: Numeric vs categorical  
✅ **Ecommerce features**: Orders, payments, devices, etc.  
✅ **Data quality**: Distributions, outliers  

## Expected Output

The script will provide:
- Column names and types
- Missing value counts
- Churn label analysis
- Sample data preview
- Summary statistics
- Ecommerce feature identification

## Next Steps

After examination:
1. ✅ Verify churn label exists (or can be derived)
2. ✅ Check data quality is good
3. ✅ Proceed to Section 2.2 (Evaluate dataset quality)
4. ✅ Then Section 2.3 (Prepare dataset locally)

## Troubleshooting

**If file not found**:
- Check the exact filename after download
- Look in Downloads folder
- Verify file was extracted from ZIP

**If script errors**:
- Ensure pandas is installed: `pip install pandas`
- Check Python version (3.8+)
- Verify CSV file is valid
