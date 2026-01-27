# Recommender Model Deployment Guide

## Overview

This guide provides a **reusable, automated system** for managing recommender model retraining, testing, and deployment with proper versioning, backup, and rollback capabilities.

## Files

1. **`recommender_deployment_manager.py`** - Python module with deployment management functions
2. **`Recommender-Retrain-Template.ipynb`** - Reusable notebook template for retraining

## Quick Start

### 1. Upload to OCI Data Science Notebook

Upload these files to your Data Science notebook session:
- `recommender_deployment_manager.py` → `/home/datascience/`
- `Recommender-Retrain-Template.ipynb` → `/home/datascience/`

### 2. First Time Setup

Open `Recommender-Retrain-Template.ipynb` and update **Cell 3** with your database credentials:

```python
connection_parameters = {
    "user_name": "ADMIN",
    "password": "your_password",  # ⚠️ Use OCI Vault in production!
    "service_name": "your_service_medium",
    "wallet_location": "/path/to/wallet"
}
```

### 3. Run the Notebook

Every time you want to retrain:

1. **Run Cells 0-11** sequentially
   - Cells 0-2: Setup, backup current version
   - Cells 3-8: Train new model
   - Cells 9-10: Deploy to TEST endpoint
   - Cell 11: Test the new model

2. **Validate Testing Results**
   - Check Cell 11 output
   - Test endpoint manually if needed

3. **Make Decision:**
   - ✅ **Cell 12**: Promote to production (if tests pass)
   - ❌ **Cell 13**: Rollback (if issues found)

## Features

### ✅ Automatic Versioning

- Each retraining creates a new version (v1, v2, v3...)
- Version numbers auto-increment
- No manual tracking needed

### 📦 Automatic Backups

Before each training, the system backs up:
- Previous model artifacts
- Operator results (CSV, HTML report, **and a report with recommendations for new users**)
- Deployment metadata (model OCID, endpoint URL)

**New-user support:** The ADS Recommender Operator may write a report with recommendations for **new users**. Use `recommender_new_user_fallback.py` and the score.py in **BLUEGREEN_CELLS_TO_ADD.md** (section "New-user recommendations") to: (1) at train time, build `new_user_fallback.pkl` from that report or from a popularity-based fallback from `recommendations.csv`; (2) at inference, have `score.py` return that fallback when `user_id` is not in the main model.

Backups are stored in: `/home/datascience/backups/`

### 🧪 Blue-Green Deployment

- **Production deployment** continues running during testing
- **Test deployment** created for validation
- No downtime during retraining
- Easy promotion or rollback

### ⏪ Easy Rollback

Multiple rollback options:
1. **Reject new version**: Run Cell 13 to keep production unchanged
2. **Rollback to specific version**: Use Cell 15 to restore any previous version

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Backup Current Production (Cell 2)                 │
├─────────────────────────────────────────────────────────────┤
│ Creates: /home/datascience/backups/v2_20260125_143022/     │
│   ├── recommender_model_artifact/                          │
│   ├── results/                                             │
│   └── metadata.json                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Train New Model (Cells 3-8)                        │
├─────────────────────────────────────────────────────────────┤
│ - Extract fresh data from database                         │
│ - Run ADS Recommender Operator                             │
│ - Create model artifact                                    │
│                                                             │
│ Result: New v3 artifacts ready for deployment              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Deploy to TEST (Cells 9-10)                        │
├─────────────────────────────────────────────────────────────┤
│ Production (v2): ✅ Still running                           │
│ Test (v3):       🧪 New endpoint created                    │
│                                                             │
│ Both endpoints available for comparison                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Validate (Cell 11)                                 │
├─────────────────────────────────────────────────────────────┤
│ - Test known users                                         │
│ - Test unknown users                                       │
│ - Compare with production if needed                        │
│ - Manual validation as needed                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │   Tests Pass?     │
                    └─────────┬─────────┘
                    │                   │
            ✅ Yes  │                   │ ❌ No
                    ↓                   ↓
┌──────────────────────────┐  ┌──────────────────────────┐
│ Cell 12: PROMOTE         │  │ Cell 13: ROLLBACK        │
├──────────────────────────┤  ├──────────────────────────┤
│ - Update production to   │  │ - Delete test deployment │
│   use v3 model           │  │ - Keep production on v2  │
│ - Keep same endpoint URL │  │ - Restore v2 artifacts   │
│ - Delete test deployment │  │ - No impact to prod      │
│                          │  │                          │
│ Production: v3 ✅        │  │ Production: v2 ✅        │
└──────────────────────────┘  └──────────────────────────┘
```

## State Management

The deployment manager tracks state in:
```
/home/datascience/backups/deployment_state.json
```

State includes:
- Current version number
- Production deployment info (OCID, endpoint, model version)
- Test deployment info (if active)
- Deployment history

### View Current State

Run in a notebook cell:

```python
from recommender_deployment_manager import RecommenderDeploymentManager

manager = RecommenderDeploymentManager()
print(manager.get_deployment_summary())
```

Output:
```
============================================================
🎯 Product Recommender - Deployment Status
============================================================

✅ PRODUCTION (v2)
   Model: ocid1.datasciencemodel.oc1...
   Endpoint: https://modeldeployment.ap-singapore-1...
   Deployed: 2026-01-20T14:30:00

🧪 TEST: No test deployment

📊 Current Version: v2
📦 Total Deployments: 2
============================================================
```

## Advanced Usage

### List All Backups

```python
from recommender_deployment_manager import RecommenderDeploymentManager, print_backups

manager = RecommenderDeploymentManager()
backups = manager.list_backups()
print_backups(backups)
```

### Manual Rollback to Specific Version

```python
# Rollback artifacts to v2
manager.rollback_artifacts(version=2)

# To also update the deployment, you'll need to manually deploy
# the rolled-back artifacts using the standard deployment flow
```

### Customize Deployment Resources

In Cell 10, modify the deployment parameters:

```python
test_deployment = manager.deploy_model(
    model=model,
    model_id=model_id,
    version=next_version,
    is_test=True,
    instance_shape="VM.Standard.E4.Flex",
    ocpus=2,  # ⬅️ Increase OCPUs
    memory_gb=32  # ⬅️ Increase memory
)
```

### Skip Test Deployment (Deploy Directly to Production)

⚠️ **Not recommended, but possible:**

In Cell 9, change `is_test=False`:

```python
model_id = manager.save_new_model(
    model=model,
    version=next_version,
    num_users=num_users,
    num_products=num_products,
    is_test=False  # ⬅️ Skip testing
)
```

## Best Practices

### 1. Always Test First
- Never skip the test deployment step
- Validate recommendations with real users if possible
- Check edge cases (unknown users, empty results)

### 2. Monitor Production
- Set up OCI monitoring for your production endpoint
- Track response times and error rates
- Set up alerts for failures

### 3. Keep Backups
- Don't delete backup directories manually
- Backups are cheap (a few MB each)
- They're invaluable for troubleshooting

### 4. Clean Up Old Resources
After successful promotion, you can delete old models from Model Catalog:
- Go to OCI Console → Data Science → Model Catalog
- Find old versions (v1, v2, etc.) that are no longer needed
- Delete them to reduce clutter

### 5. Secure Your Credentials
Instead of hardcoding passwords in Cell 3:

```python
# Option 1: Use OCI Vault
from ads.secrets.oraclevault import OracleVaultSecretKeeper

secret_keeper = OracleVaultSecretKeeper(
    vault_id="ocid1.vault.oc1...",
    secret_id="ocid1.vaultsecret.oc1..."
)
password = secret_keeper.get_secret()

# Option 2: Use environment variables
import os
password = os.environ.get("DB_PASSWORD")

# Option 3: Read from secure file
with open("/home/datascience/.secrets/db_config.json") as f:
    config = json.load(f)
    password = config["password"]
```

## Troubleshooting

### Issue: "No previous version to backup"
**Solution**: This is normal on first run. The system will start tracking from v1.

### Issue: "Test deployment failed"
**Solution**: Check OCI logs for the deployment. Common causes:
- Insufficient compute quota
- Conda environment issues
- Model artifact corruption

### Issue: "Cannot promote to production - no test deployment"
**Solution**: Make sure you run Cells 9-10 first to create the test deployment.

### Issue: "Rollback failed - backup not found"
**Solution**: The backup directory may have been deleted. Check:
```bash
ls -la /home/datascience/backups/
```

### Issue: Production endpoint not responding after update
**Solution**: 
1. Check deployment status in OCI Console
2. Look at deployment logs
3. If critical, manually update deployment to use previous model OCID
4. Use rollback procedure in Cell 13

## API Reference

### RecommenderDeploymentManager

#### `__init__(project_name, backup_root, artifact_dir, results_dir)`
Initialize the deployment manager.

#### `get_next_version() -> int`
Get the next version number to use.

#### `backup_current_artifacts(version) -> Path`
Backup current artifacts and return backup directory path.

#### `save_new_model(model, version, num_users, num_products, is_test) -> str`
Save model to OCI Model Catalog and return model OCID.

#### `deploy_model(model, model_id, version, is_test, instance_shape, ocpus, memory_gb) -> ModelDeployment`
Deploy model to OCI Model Deployment and return deployment object.

#### `promote_to_production(test_deployment_id)`
Promote test deployment to production.

#### `cleanup_test_deployment()`
Delete the test deployment.

#### `rollback_artifacts(version) -> bool`
Rollback local artifacts to a specific version.

#### `get_deployment_summary() -> str`
Get a formatted summary of current deployments.

#### `list_backups() -> List[Dict]`
List all available backups.

## Support

For issues or questions:
1. Check this guide first
2. Review OCI Data Science documentation
3. Check ADS documentation: https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/

## Version History

- **v1.0** (2026-01-25): Initial release with automated versioning and blue-green deployment
