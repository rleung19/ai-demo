# Recommender Deployment Management

## Overview

This system adds **blue-green deployment** capability to your existing recommender model notebook **without changing any of your working training code**.

## The Problem We Solved

- ✅ **Backup**: Automatically backup before retraining
- ✅ **Versioning**: Track v1, v2, v3... automatically
- ✅ **Testing**: Deploy to TEST endpoint before production
- ✅ **Rollback**: One-click rollback if issues found
- ✅ **Zero downtime**: Production keeps running during testing
- ✅ **Same URL**: Endpoint URL doesn't change when promoting

## Files in This Directory

### Core Files (Use These)

| File | Purpose | Use |
|------|---------|-----|
| `recommender_deployment_manager.py` | Python module with all deployment logic | Upload to `/home/datascience/` |
| **`BLUEGREEN_CELLS_TO_ADD.md`** | **START HERE**: The 7 cells to ADD to YOUR notebook. No training code — your code stays yours. | **Use this** |
| `INTEGRATION_GUIDE.md` | Detailed integration instructions | Optional |
| `QUICK_INTEGRATION.md` | Quick reference | Optional |

### Reference Files

| File | Purpose |
|------|---------|
| `RECOMMENDER_DEPLOYMENT_GUIDE.md` | Complete documentation of the system |
| `FIRST_TIME_SETUP.md` | First-time setup instructions |
| `FIXES_APPLIED.md` | History of fixes and issues |

### Legacy / Do Not Use

| File | Status | Why |
|------|--------|-----|
| `Recommender-with-BlueGreen.ipynb` | ❌ **Do not use** | Training code was changed and caused errors. Use `BLUEGREEN_CELLS_TO_ADD.md` instead. |
| `Recommender-Retrain-Template.ipynb` | ❌ Obsolete | Missing import feature |
| `Recommender-Retrain-Template-v2.ipynb` | ❌ Don't use | Had bugs in training code |

## Quick Start

### Recommended: Add Cells to YOUR Notebook

1. Upload `recommender_deployment_manager.py` to `/home/datascience/`

2. Open **`BLUEGREEN_CELLS_TO_ADD.md`**

3. **Add** the 7 cells to **your** existing notebook:
   - 2 cells at the beginning (after setup, before data extraction)
   - 5 cells at the end (after model prep; remove your `model.save()` and `model.deploy()`)

4. Your training code stays **100% unchanged**. We do not provide or modify any of it.

## What Gets Created

### Directory Structure

```
/home/datascience/
├── recommender_deployment_manager.py    ← The manager module
├── backups/
│   ├── deployment_state.json            ← Tracks versions
│   ├── v1_20260125_121732/              ← Backup of v1
│   │   ├── recommender_model_artifact/
│   │   ├── results/
│   │   └── metadata.json
│   ├── v2_20260125_143022/              ← Backup of v2
│   │   └── ...
│   └── ...
├── recommender_model_artifact/          ← Current model artifacts
├── results/                             ← Operator results
└── Recommender-with-BlueGreen.ipynb     ← Your notebook
```

### State Tracking

`backups/deployment_state.json`:
```json
{
  "current_version": 2,
  "production_deployment": {
    "deployment_id": "ocid1...",
    "model_id": "ocid1...",
    "endpoint": "https://...",
    "version": 2,
    "status": "PRODUCTION"
  },
  "test_deployment": null,
  "deployment_history": [...]
}
```

## Workflow

### First Time Only

If you have an existing deployment, add one cell before Cell 0:

```python
manager.import_existing_deployment(
    deployment_id="ocid1.datasciencemodeldeployment...",
    model_id="ocid1.datasciencemodel...",
    endpoint="https://modeldeployment...",
    version=1,
    description="Original model"
)
```

### Every Retraining

```
1. Cell 0-1:   Backup current version
2. Cell 2-11:  Train new model (your code)
3. Cell 12:    Save to catalog (TEST)
4. Cell 13:    Deploy to TEST endpoint
5. Cell 14:    Test the endpoint
6. Decision:
   - Tests pass? → Cell 15 (Promote)
   - Tests fail? → Cell 16 (Rollback)
```

## Key Benefits

### 1. Your Code Stays Unchanged

The training code (data extraction, operator run, model prep) is **100% your proven working code**. The manager only adds deployment capabilities on top.

### 2. Blue-Green Deployment

```
Before Promotion:
- Production: v1 (serving traffic)
- Test: v2 (being validated)

After Promotion:
- Production: v2 (serving traffic)
- Test: deleted (cleaned up)
- v1 backup: available for rollback
```

### 3. Automatic Versioning

No manual tracking:
- v1 → v2 → v3 → v4...
- Each version backed up automatically
- Complete deployment history

### 4. Easy Rollback

If v2 has issues:
```python
manager.rollback_artifacts(version=1)
```

Done! Back to v1.

## Deployment Patterns

### Pattern 1: Standard Blue-Green

```python
# Deploy to TEST
test_deployment = manager.deploy_model(..., is_test=True)

# Test thoroughly
results = test_deployment.predict(...)

# If good → Promote
manager.promote_to_production()

# If bad → Rollback
manager.cleanup_test_deployment()
```

### Pattern 2: Direct to Production (Skip Testing)

⚠️ **Not recommended, but possible:**

```python
model_id = manager.save_new_model(..., is_test=False)
deployment = manager.deploy_model(..., is_test=False)
```

This updates production directly (no TEST endpoint).

### Pattern 3: Long-Running Test Period

```python
# Deploy v2 to TEST on Monday
test_deployment = manager.deploy_model(..., is_test=True)

# Test all week with real users hitting TEST endpoint

# Friday: Tests pass
manager.promote_to_production()

# Production v1 ran all week, v2 takes over Friday
```

## API Reference

### RecommenderDeploymentManager

#### Key Methods

```python
manager = RecommenderDeploymentManager()

# Get next version number
next_version = manager.get_next_version()  # Returns: 2

# Backup artifacts
backup_dir = manager.backup_current_artifacts(version=1)

# Save model to catalog
model_id = manager.save_new_model(
    model=model,
    version=2,
    num_users=4926,
    num_products=320,
    is_test=True
)

# Deploy model
deployment = manager.deploy_model(
    model=model,
    model_id=model_id,
    version=2,
    is_test=True,
    instance_shape="VM.Standard.E4.Flex",
    ocpus=1,
    memory_gb=16
)

# Promote to production
manager.promote_to_production()

# Cleanup test deployment
manager.cleanup_test_deployment()

# Rollback artifacts
manager.rollback_artifacts(version=1)

# Get status summary
print(manager.get_deployment_summary())

# List backups
backups = manager.list_backups()
```

## Troubleshooting

### Issue: "No module named 'recommender_deployment_manager'"

**Solution:** Upload `recommender_deployment_manager.py` to `/home/datascience/`

### Issue: "Next version: v1" but I have a deployment

**Solution:** Run the import cell to register your existing deployment

### Issue: Promotion fails

**Solution:** Check that test deployment exists:
```python
print(manager.state['test_deployment'])
```

### Issue: Want to skip a version number

**Solution:** Manually update state:
```python
manager.state['current_version'] = 5
manager._save_state()
# Next version will be 6
```

## Best Practices

1. ✅ **Always test first** - Never skip the TEST deployment
2. ✅ **Keep backups** - Don't delete backup directories
3. ✅ **Monitor production** - Set up OCI monitoring/alerts
4. ✅ **Clean up old models** - Delete old model versions from catalog after promotion
5. ✅ **Document changes** - Note what changed in each version

## Support

For issues:
1. Check `INTEGRATION_GUIDE.md` for detailed instructions
2. Check `TROUBLESHOOTING` section above
3. Review `FIXES_APPLIED.md` for known issues
4. Check OCI logs for deployment failures

## Version History

- **v1.0** (2026-01-25): Initial release
  - Blue-green deployment support
  - Automatic versioning and backup
  - Integration with existing notebooks
  - Bug fixes for database queries and model preparation

## License

Use freely for your recommender model deployments.
