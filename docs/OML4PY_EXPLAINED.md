# OML4Py Explained: How It Works and Where to Use It

## Key Question: Where Does Model Training Happen?

**Answer**: Model training happens **in the Oracle ADB database** (remotely), not on your local machine. OML4Py is the Python interface that connects to ADB and executes ML operations **inside the database**.

## How OML4Py Works

### 1. OML4Py Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Your Local Machine / OML Notebooks Server            │
│                                                         │
│  Python Script with OML4Py                            │
│  import oml                                             │
│  oml.sync(view='CHURN_TRAINING_DATA')                  │
│  xgb_model = oml.xgb('classification')                 │
│  xgb_model.fit(X_oml, y_oml)                           │
└────────────────────┬──────────────────────────────────┘
                     │
                     │ SQL/OML API calls
                     │
┌────────────────────▼──────────────────────────────────┐
│  Oracle ADB Serverless (Remote Database)               │
│                                                         │
│  ┌─────────────────────────────────────────────┐     │
│  │  OML Engine (In-Database ML)                  │     │
│  │  - XGBoost training happens HERE             │     │
│  │  - Data stays in database                    │     │
│  │  - Model stored in OML Datastore             │     │
│  └─────────────────────────────────────────────┘     │
│                                                         │
│  ┌─────────────────────────────────────────────┐     │
│  │  Database Tables/Views                       │     │
│  │  - CHURN_TRAINING_DATA (view)                │     │
│  │  - CHURN_USER_FEATURES (view)                │     │
│  │  - CHURN_PREDICTIONS (table)                 │     │
│  └─────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

**Key Point**: The actual XGBoost training happens **inside Oracle ADB**, not on your local machine. OML4Py is just the Python interface that sends commands to the database.

### 2. Where Can OML4Py Be Used?

#### Option A: OML Notebooks UI (Recommended) ✅

**Location**: Oracle Cloud Console → ADB → OML Notebooks

**How it works**:
1. You access OML Notebooks through web browser
2. OML Notebooks runs on Oracle's servers (connected to your ADB)
3. OML4Py is **pre-installed** and **pre-configured**
4. You run Python cells that use `import oml`
5. Training happens in ADB (remote)

**Advantages**:
- ✅ OML4Py already installed and configured
- ✅ Direct connection to ADB (no setup needed)
- ✅ Web-based interface (no local installation)
- ✅ Pre-configured environment

**Usage**:
```python
# In OML Notebooks UI (web browser)
%python
import oml
train_data = oml.sync(view='CHURN_TRAINING_DATA')
xgb_model = oml.xgb('classification')
xgb_model.fit(X_oml, y_oml)  # Training happens in ADB
```

#### Option B: Standalone Python (Limited) ⚠️

**Location**: Your local machine

**How it works**:
1. You install OML4Py Python package locally
2. You configure connection to ADB
3. You run Python scripts that use `import oml`
4. Training still happens in ADB (remote), but you control it from local machine

**Challenges**:
- ⚠️ OML4Py package may not be publicly available
- ⚠️ Requires complex setup and configuration
- ⚠️ May not work outside Oracle's infrastructure
- ⚠️ Typically only works in OML Notebooks environment

**Reality**: Most users **cannot** use OML4Py standalone. It's designed for OML Notebooks.

### 3. What I Created: Two Versions

#### Version 1: Standalone Script (`scripts/train_churn_model.py`)

**Purpose**: Complete Python script with all logic

**Where to run**: 
- **Intended for**: OML Notebooks (copy/paste or exec)
- **Can also work**: Standalone if OML4Py is available locally (rare)

**How to use in OML Notebooks**:
```python
%python
# Option 1: Execute the script
exec(open('scripts/train_churn_model.py').read())

# Option 2: Copy/paste functions as needed
```

**What it does**:
- Checks for OML4Py
- Connects to ADB
- Loads data from views
- Trains model (in ADB)
- Saves model (in ADB)

#### Version 2: Notebook Cells (`oml-notebooks/train_churn_model_notebook.py`)

**Purpose**: Cell-by-cell version for OML Notebooks UI

**Where to run**: **OML Notebooks UI** (web browser)

**How to use**:
1. Open OML Notebooks in Oracle Cloud Console
2. Create new notebook
3. Copy each cell from `train_churn_model_notebook.py`
4. Paste into notebook as Python cells
5. Run cells sequentially

**What it does**: Same as Version 1, but organized as separate cells

## The Training Process: Step by Step

### When You Run the Script in OML Notebooks:

1. **You execute** (in OML Notebooks UI):
   ```python
   train_data = oml.sync(view='CHURN_TRAINING_DATA')
   ```
   - **What happens**: OML4Py sends SQL query to ADB
   - **Where**: Query executes in ADB
   - **Result**: Data reference returned to Python

2. **You execute**:
   ```python
   xgb_model = oml.xgb('classification')
   xgb_model.fit(X_oml, y_oml)
   ```
   - **What happens**: OML4Py sends training command to ADB
   - **Where**: XGBoost training happens **inside ADB**
   - **Result**: Model trained and stored in ADB's OML engine

3. **You execute**:
   ```python
   oml.ds.save({'model': xgb_model}, 'churn_xgboost_v1')
   ```
   - **What happens**: Model saved to OML Datastore
   - **Where**: Stored in ADB (not on your machine)
   - **Result**: Model persisted in database

### Key Insight: Data Never Leaves ADB

- ✅ Training data stays in ADB
- ✅ Model training happens in ADB
- ✅ Model stored in ADB
- ✅ Predictions happen in ADB
- ✅ Only results/metadata come back to Python

## Why Two Versions?

### Standalone Script (`train_churn_model.py`)
- **Use case**: If you want to run everything at once
- **Best for**: Automated workflows, testing
- **Format**: One complete Python script

### Notebook Cells (`train_churn_model_notebook.py`)
- **Use case**: Step-by-step execution in OML Notebooks UI
- **Best for**: Learning, debugging, experimentation
- **Format**: Separate cells you can run individually

## Can You Train Remotely Without OML Notebooks UI?

### Short Answer: **Not easily**

**Why**:
- OML4Py is typically **only available** in OML Notebooks environment
- It's not a standard Python package you can `pip install`
- Oracle provides it as part of OML Notebooks infrastructure

### Alternative: Use `oracledb` + Local Training

If you can't use OML4Py, you can:
1. Use `oracledb` to query data from ADB
2. Train model locally with sklearn/xgboost
3. Save model locally (not in OML Datastore)
4. Use model for predictions locally

**Trade-off**: 
- ❌ Model not stored in ADB
- ❌ Can't use OML Datastore
- ❌ Training happens locally (slower for large data)
- ✅ Works without OML Notebooks

## Recommended Workflow

### For Production Model Training:

1. **Use OML Notebooks UI** (recommended)
   - Access via Oracle Cloud Console
   - Run `train_churn_model_notebook.py` cells
   - Model trained and stored in ADB

2. **For API/Scoring**:
   - Use `oracledb` (Node.js/Python)
   - Read predictions from `CHURN_PREDICTIONS` table
   - No need for OML4Py in API server

### For Development/Testing:

1. **Use OML Notebooks UI** for model training
2. **Use local scripts** (`validate_model_performance.py`) for quick validation
3. **Use `oracledb`** for data access in API

## Summary

| Aspect | OML Notebooks UI | Standalone Python |
|--------|------------------|-------------------|
| **OML4Py Available** | ✅ Yes (pre-installed) | ⚠️ Usually No |
| **Where Training Happens** | ADB (remote) | ADB (remote) or Local |
| **Model Storage** | OML Datastore (in ADB) | OML Datastore or Local |
| **Setup Required** | None (web-based) | Complex (if possible) |
| **Recommended For** | Model training | API/data access |

## Bottom Line

**The scripts I created are designed to run in OML Notebooks UI**, where OML4Py is available. The model training happens **remotely in your ADB**, not on your local machine. The notebook version makes it easy to run step-by-step in the OML Notebooks web interface.

**For the API server** (Section 4), you'll use `oracledb` (not OML4Py) to read predictions from the `CHURN_PREDICTIONS` table that was populated by the scoring script.

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  STEP 1: Model Training (OML Notebooks UI)             │
│                                                         │
│  1. Open OML Notebooks in Oracle Cloud Console        │
│  2. Copy cells from train_churn_model_notebook.py     │
│  3. Run cells → Model trains in ADB                    │
│  4. Model saved to OML Datastore                       │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 2: Model Scoring (OML Notebooks UI)             │
│                                                         │
│  1. Run score_churn_model.py in OML Notebooks         │
│  2. Loads model from OML Datastore                     │
│  3. Scores all users → Predictions stored in ADB       │
│  4. CHURN_PREDICTIONS table populated                  │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 3: API Server (Your Local Machine / Server)     │
│                                                         │
│  1. Uses oracledb (NOT OML4Py)                        │
│  2. Reads from CHURN_PREDICTIONS table                  │
│  3. Returns predictions to frontend                    │
│  4. No model training needed (already done)            │
└─────────────────────────────────────────────────────────┘
```

## Important Clarifications

### ❌ What I Did NOT Do:
- I did **NOT** train a model remotely from your local machine
- I did **NOT** assume OML4Py works standalone
- I did **NOT** create scripts that run without OML Notebooks

### ✅ What I DID Do:
- Created scripts **designed for OML Notebooks UI**
- Created notebook cell version for easy copy/paste
- Made scripts that will work when you run them in OML Notebooks
- Created API-ready data structure (CHURN_PREDICTIONS table)

### 🎯 What You Need to Do:
1. **Open OML Notebooks** in Oracle Cloud Console
2. **Copy cells** from `oml-notebooks/train_churn_model_notebook.py`
3. **Run in OML Notebooks** → Model trains in ADB
4. **Run scoring script** → Predictions stored in ADB
5. **API reads** from CHURN_PREDICTIONS table (no OML4Py needed)
