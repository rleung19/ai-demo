# Task 2.5: Create Data Ingestion Script

## Status

✅ **Completed**: Data ingestion script created

## What Was Created

### Data Ingestion Script
- **File**: `scripts/ingest_churn_data.py`
- **Purpose**: Loads CSV files into Oracle ADB OML schema tables

### Features

1. **Loads Two Datasets**:
   - `data/processed/churn_dataset_training.csv` → `OML.CHURN_DATASET_TRAINING`
   - `data/processed/churn_dataset_mapped.csv` → `OML.USER_PROFILES`

2. **Data Processing**:
   - Maps CSV column names to Oracle schema (e.g., `Age` → `AGE`)
   - Handles data type conversions
   - Validates CHURNED values (0 or 1)
   - Replaces NaN with NULL for Oracle

3. **Connection Management**:
   - Uses connection pattern from `test-python-connection.py`
   - Supports both thick and thin mode
   - Handles wallet-based authentication

4. **Error Handling**:
   - Validates CSV files exist
   - Checks database connection
   - Provides clear error messages
   - Rolls back on failure

5. **Performance**:
   - Uses `executemany()` for bulk inserts
   - Truncates tables before loading (ensures clean data)
   - Verifies row counts after insertion

## Prerequisites

1. **Tables Created**: Run `sql/create_churn_tables.sql` first
2. **CSV Files**: Ensure CSV files exist in `data/processed/`
3. **Environment**: `.env` file configured with ADB credentials
4. **Dependencies**: 
   - `oracledb` (pip install oracledb)
   - `pandas` (pip install pandas)
   - `python-dotenv` (pip install python-dotenv)

## Usage

### Basic Usage

```bash
python scripts/ingest_churn_data.py
```

### What It Does

1. **Connects to ADB** as OML user
2. **Loads Training Data**:
   - Reads `churn_dataset_training.csv`
   - Truncates `OML.CHURN_DATASET_TRAINING`
   - Inserts ~45,858 rows
   - Verifies row count

3. **Loads User Profiles**:
   - Reads `churn_dataset_mapped.csv`
   - Truncates `OML.USER_PROFILES`
   - Inserts ~4,142 rows
   - Verifies row count

4. **Reports Summary**:
   - Success/failure for each table
   - Row counts
   - Next steps

## Expected Output

```
============================================================
Churn Data Ingestion Script
============================================================
Started at: 2026-01-XX XX:XX:XX
✓ Loaded .env file from: /path/to/.env
✓ Oracle client initialized: /opt/oracle/instantclient_23_3 (thick mode)
✓ Connected to ADB as OML

============================================================
Loading Training Data
============================================================
Reading CSV: data/processed/churn_dataset_training.csv
✓ Loaded 45,858 rows from CSV
✓ Mapped column names to Oracle schema
✓ Prepared data for Oracle
✓ Cleared existing training data

Inserting 45,858 rows into OML.CHURN_DATASET_TRAINING...
✓ Successfully inserted 45,858 rows
✓ Verified: 45,858 rows in table

============================================================
Loading User Profiles
============================================================
Reading CSV: data/processed/churn_dataset_mapped.csv
✓ Loaded 4,142 rows from CSV
✓ Mapped column names to Oracle schema
✓ Prepared data for Oracle
✓ Cleared existing user profiles

Inserting 4,142 rows into OML.USER_PROFILES...
✓ Successfully inserted 4,142 rows
✓ Verified: 4,142 rows in table

============================================================
Ingestion Summary
============================================================
Training Data:    ✓ SUCCESS
User Profiles:    ✓ SUCCESS

✓ All data loaded successfully!

Next steps:
1. Validate data (Task 2.6)
2. Create feature engineering views (Task 2.7)
3. Train model (Task 3.x)

✓ Connection closed
Completed at: 2026-01-XX XX:XX:XX
```

## Troubleshooting

### Error: CSV file not found
- **Solution**: Ensure CSV files exist in `data/processed/`
- Run `scripts/prepare_dataset_for_oml.py` and `scripts/create_hybrid_datasets.py` first

### Error: Table does not exist
- **Solution**: Run `sql/create_churn_tables.sql` first to create tables

### Error: Connection failed
- **Solution**: Check `.env` file configuration
- Verify ADB instance is running
- Test connection with `scripts/test-python-connection.py`

### Error: Invalid CHURNED values
- **Solution**: Script will automatically fix invalid values (set to 0)
- Check CSV data quality if this occurs

## Column Mapping

The script automatically maps CSV column names to Oracle schema:

| CSV Column | Oracle Column |
|------------|---------------|
| Age | AGE |
| Gender | GENDER |
| Country | COUNTRY |
| ... | ... |
| Churned | CHURNED |
| USER_ID | USER_ID |

## Data Validation

The script performs basic validation:
- ✅ CHURNED values must be 0 or 1
- ✅ USER_ID must be string
- ✅ NaN values converted to NULL
- ✅ Row count verification after insertion

## Next Steps

1. ✅ **Task 2.5 Complete**: Data ingestion script created
2. ⏳ **Task 2.6**: Validate data loaded correctly (row counts, data types, constraints)
3. ⏳ **Task 2.7**: Create feature engineering views in OML schema

## Related Documentation

- `docs/DATA_MAPPING_DOCUMENT.md` - Column mappings and data types
- `sql/create_churn_tables.sql` - Table schema
- `scripts/test-python-connection.py` - Connection testing
