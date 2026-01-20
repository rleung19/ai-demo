# Automating OML Model Training

## Overview

This document covers automation options for OML model training. **Note**: The recommended approach is to use OML4Py in OML Notebooks (see `docs/HOW_TO_USE_OML4PY.md`). This document covers alternative automation approaches.

## Option 1: Scheduled Notebooks (Easiest) ✅

**What it is**: OML Notebooks has built-in scheduling that can run notebooks automatically.

**How it works**:
1. Create your notebook in OML Notebooks UI (one-time setup)
2. Configure schedule (daily, weekly, etc.) in the UI
3. Notebook runs automatically on schedule
4. Results stored in database

**Pros**:
- ✅ Simple setup
- ✅ No external infrastructure needed
- ✅ Works with OML4Py
- ✅ Model stored in OML Datastore

**Cons**:
- ⚠️ Still requires initial UI setup
- ⚠️ Limited error handling/logging visibility
- ⚠️ Less flexible for complex pipelines

**Best for**: Regular retraining (daily/weekly) with minimal setup.

---

## Option 2: Oracle Scheduler + EXTPROC (Recommended for Automation) 🎯

**What it is**: Run Python scripts directly via Oracle Database Scheduler using external procedure containers.

**How it works**:
1. Store Python script in database or accessible location
2. Create Oracle Scheduler job
3. Job executes Python script with database context
4. Script can use OML4Py (if available) or oracledb

**Pros**:
- ✅ Fully automated (no UI needed after setup)
- ✅ Integrates with database scheduler
- ✅ Can use OML4Py if available
- ✅ Can schedule via SQL/PL/SQL

**Cons**:
- ⚠️ Requires EXTPROC setup
- ⚠️ Security/permission configuration needed
- ⚠️ Script must be accessible to database

**Best for**: Production automation with database integration.

**Implementation**: See `scripts/train_churn_model_scheduled.py` (created below)

---

## Option 3: Local Training + Database Storage (Works Without OML4Py) 🔄

**What it is**: Train model locally using `oracledb` + `xgboost`, then store results in database.

**How it works**:
1. Python script connects to ADB via `oracledb`
2. Pulls training data from database
3. Trains model locally with XGBoost
4. Stores model metadata/predictions in database
5. Can be scheduled via cron/Airflow/etc.

**Pros**:
- ✅ Works without OML4Py
- ✅ Full control over training process
- ✅ Can run anywhere (local/server/cloud)
- ✅ Easy to schedule (cron, Airflow, etc.)

**Cons**:
- ❌ Model not in OML Datastore (stored locally or as BLOB)
- ❌ Data must be pulled to local machine
- ❌ Training happens locally (slower for large data)
- ❌ Can't use OML4Py in-database features

**Best for**: When OML4Py is not available or you need full control.

**Implementation**: See `scripts/train_churn_model_local.py` (created below)

---

## Option 4: REST API for Batch Scoring (Scoring Only) 📡

**What it is**: Use OML Services REST API to trigger batch scoring jobs.

**How it works**:
1. Deploy model via OML Services (creates REST endpoint)
2. Submit batch scoring job via REST API
3. Job runs in database
4. Results stored in output table

**Pros**:
- ✅ Fully automated via REST
- ✅ Can integrate with external schedulers
- ✅ Good for production scoring

**Cons**:
- ❌ Only for scoring, not training
- ❌ Requires model deployment via OML Services
- ❌ REST API setup needed

**Best for**: Automated batch scoring of new data.

---

## Option 5: OCI Data Science + Data Integration (Enterprise) 🏢

**What it is**: Use Oracle Cloud Infrastructure services for full ML pipeline orchestration.

**How it works**:
1. Store notebooks in Object Storage
2. Define jobs in YAML
3. Orchestrate via Data Integration
4. Schedule and monitor via APIs

**Pros**:
- ✅ Enterprise-grade orchestration
- ✅ Version control, monitoring, alerting
- ✅ Full pipeline management

**Cons**:
- ❌ Complex setup
- ❌ Additional OCI services needed
- ❌ Higher cost
- ❌ Learning curve

**Best for**: Enterprise production environments with complex pipelines.

---

## Recommended Approach for This Project

### For Model Training:

**Option 2 (Oracle Scheduler + EXTPROC)** or **Option 3 (Local Training)** depending on:
- If OML4Py is available in your environment → Use Option 2
- If OML4Py is not available → Use Option 3

### For Model Scoring:

**Option 3 (Local Script)** - Simple Python script that:
1. Connects via `oracledb`
2. Loads model (from file or database)
3. Scores users
4. Stores predictions in `CHURN_PREDICTIONS` table

### For Scheduling:

- **Option 2**: Use Oracle Scheduler (if using EXTPROC)
- **Option 3**: Use cron, systemd, or Airflow (if using local training)

---

## Implementation Examples

I've created an automation script:

1. **`scripts/train_churn_model_local.py`**: Local training (works without OML4Py)
   - Connects via `oracledb`
   - Trains model locally with XGBoost
   - Stores metadata and predictions in database
   - Full logging and error handling
   - Ready for scheduling

**Setup Guide**: See `docs/AUTOMATION_SETUP_GUIDE.md` for detailed instructions.

**Scheduling Options**:
- Cron (Linux/Mac) - Simplest
- Systemd Timer (Linux) - More control
- Airflow DAG - Production pipelines
- GitHub Actions - CI/CD integration
- Oracle Scheduler - Database integration (if EXTPROC available)

---

## Comparison Table

| Option | Automation Level | OML4Py Required | Setup Complexity | Best For |
|--------|------------------|-----------------|------------------|----------|
| **Scheduled Notebooks** | Medium | ✅ Yes | Low | Simple retraining |
| **Oracle Scheduler + EXTPROC** | High | Optional | Medium | Database integration |
| **Local Training** | High | ❌ No | Low | Full control |
| **REST API** | High | ✅ Yes (for deployment) | Medium | Batch scoring |
| **OCI Data Science** | Very High | Optional | High | Enterprise pipelines |

---

## Next Steps

1. **Choose your approach** based on requirements
2. **Review implementation scripts** (created below)
3. **Set up scheduling** (cron, Oracle Scheduler, etc.)
4. **Test automation** with dry-run mode
5. **Monitor and alert** on failures

---

## Security Considerations

- ✅ Store credentials securely (environment variables, OCI Vault)
- ✅ Use least-privilege database users
- ✅ Encrypt connections (TLS/SSL)
- ✅ Log all automation runs
- ✅ Set up alerts for failures

---

## Monitoring & Error Handling

For any automation approach:
- Log all runs (success/failure)
- Store run metadata in database
- Set up alerts (email, Slack, etc.) on failures
- Track model performance over time
- Version control all scripts
