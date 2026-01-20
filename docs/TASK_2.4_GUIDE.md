# Task 2.4: Create Data Mapping Document

## Location

**Document**: `docs/DATA_MAPPING_DOCUMENT.md`

## What is Task 2.4?

Create a document that maps:
- **Source**: Kaggle dataset columns (dhairyajeetsingh)
- **Target**: OML schema table columns

## Purpose

The data mapping document helps:
1. **Understand transformations**: How source columns map to target columns
2. **Data type conversions**: Python types → Oracle types
3. **Column naming**: Source names → Target names
4. **Data ingestion**: Guide for loading script (Task 2.5)

## What's Included

The mapping document (`docs/DATA_MAPPING_DOCUMENT.md`) contains:

1. **Source Dataset Info**:
   - Dataset name and file location
   - Number of rows and columns

2. **Target Tables**:
   - `OML.CHURN_DATASET_TRAINING` (45,858 rows)
   - `OML.CHURN_DATASET_MAPPED` (4,142 rows)

3. **Column Mappings**:
   - Source column → Target column
   - Data type conversions
   - Notes and transformations

4. **Data Quality Notes**:
   - Missing value handling
   - Data anomaly fixes
   - Validation rules

## How to Use

1. **Review the mapping**: Check `docs/DATA_MAPPING_DOCUMENT.md`
2. **Verify mappings**: Ensure all columns are mapped correctly
3. **Use for ingestion**: Reference when creating data loading script (Task 2.5)

## Related Tasks

- **Task 1.3**: Design database schema (creates the target tables)
- **Task 2.5**: Create data ingestion script (uses this mapping)
- **Task 2.6**: Validate data loaded correctly (verifies mapping worked)

## Next Steps

After reviewing the mapping document:
1. Proceed to **Task 1.3** (Design database schema) - Create the target tables
2. Then **Task 2.5** (Create data ingestion script) - Load data using the mapping
