# Integration Guide: Adding Blue-Green Deployment to Your Working Notebook

## Overview

This guide shows how to add blue-green deployment management to your **existing working** `Recommender-2.ipynb` notebook without changing any of your proven training code.

## Strategy

- ✅ **Keep your working training code unchanged** (Cells 0-8)
- ✅ **Add deployment management** for blue-green capability
- ✅ **No code replication** - use your proven patterns

## What to Add

### Step 1: Add Import Cell at the Top

**Insert NEW CELL 0 (before your existing cells):**

```python
# Deployment Management Setup
import sys
sys.path.append('/home/datascience')
from recommender_deployment_manager import RecommenderDeploymentManager

# Initialize manager
manager = RecommenderDeploymentManager(
    project_name="Product Recommender",
    backup_root="/home/datascience/backups",
    artifact_dir="/home/datascience/recommender_model_artifact",
    results_dir="/home/datascience/results"
)

print(manager.get_deployment_summary())

# Get version numbers
next_version = manager.get_next_version()
current_version = manager.state['current_version']

print(f"\n🎯 Next version to be trained: v{next_version}")
```

### Step 2: Add Backup Cell

**Insert NEW CELL after Cell 0:**

```python
# Backup current production before training
if current_version > 0:
    print(f"📦 Backing up current production (v{current_version})...\n")
    backup_dir = manager.backup_current_artifacts(version=current_version)
    print(f"✅ Backed up v{current_version} to: {backup_dir}")
else:
    print("ℹ️  No previous version to backup (first deployment)")
```

### Step 3: Run Your Existing Training Code

**Run all your EXISTING cells unchanged:**
- Cell 1: Install packages ✅
- Cell 2: Setup & auth ✅
- Cell 3: Connection parameters ✅
- Cell 4: Extract data ✅
- Cell 5: Configure operator ✅
- Cell 6: Run operator ✅
- Cell 7: Load recommendations ✅
- Cell 8: Prepare model artifacts ✅

**STOP before your existing `model.save()` cell!**

### Step 4: Replace Deployment Cells

**Replace your existing deployment cells with these:**

#### NEW: Save to Catalog (TEST)

```python
# Save model to catalog as TEST version
print(f"💾 Saving model v{next_version} (TEST)...")

model_id = manager.save_new_model(
    model=model,
    version=next_version,
    num_users=len(users_df),
    num_products=interactions_df['product_id'].nunique(),
    is_test=True
)

print(f"✅ Model saved: {model_id}")
```

#### NEW: Deploy to TEST Endpoint

```python
# Deploy to TEST endpoint (blue-green)
print(f"🚀 Deploying v{next_version} to TEST endpoint...")

test_deployment = manager.deploy_model(
    model=model,
    model_id=model_id,
    version=next_version,
    is_test=True,
    instance_shape="VM.Standard.E4.Flex",
    ocpus=1,
    memory_gb=16
)

print(f"\n✅ TEST deployment ready!")
print(f"   Test URL: {test_deployment.url}")
print(manager.get_deployment_summary())
```

#### NEW: Test the Deployment

```python
# Test the new deployment
import json

print("🧪 Testing TEST endpoint...\n")

# Test with known user
result = test_deployment.predict({"user_id": "100773", "top_k": 5})
print("Known user test:")
print(json.dumps(result, indent=2))

# Test with unknown user
print("\nUnknown user test:")
result = test_deployment.predict({"user_id": "unknown_123", "top_k": 5})
print(json.dumps(result, indent=2))

print("\n✅ Testing complete")
print("\n💡 Review results above before promoting to production")
```

### Step 5: Decision Point - Promote or Rollback

#### Option A: Promote to Production

```python
# PROMOTE: Update production to use v{next_version}
print("🚀 Promoting to production...\n")

manager.promote_to_production()
manager.cleanup_test_deployment()

print(manager.get_deployment_summary())
print(f"\n✅ v{next_version} is now in PRODUCTION!")
```

#### Option B: Rollback

```python
# ROLLBACK: Keep production on v{current_version}
print("⏪ Rolling back...\n")

manager.cleanup_test_deployment()

if current_version > 0:
    manager.rollback_artifacts(version=current_version)
    print(f"✅ Rolled back to v{current_version}")

print(manager.get_deployment_summary())
```

## Cell Numbering After Integration

Here's what your notebook will look like:

```
NEW Cell 0:  Import and initialize manager
NEW Cell 1:  Backup current production

(Your existing cells, renumbered)
Cell 2:  !pip install oracle-ads[recommender]
Cell 3:  Setup and auth
Cell 4:  Connection parameters
Cell 5:  Extract interactions data
Cell 6:  Extract users data
Cell 7:  Extract items data
Cell 8:  Configure operator
Cell 9:  Run operator
Cell 10: Load recommendations
Cell 11: Prepare model artifacts

(New deployment cells)
NEW Cell 12: Save to catalog (TEST)
NEW Cell 13: Deploy to TEST endpoint
NEW Cell 14: Test the deployment
NEW Cell 15: PROMOTE to production
NEW Cell 16: OR ROLLBACK
```

## What Changes in Your Original Code

**NOTHING!** Your training code (Cells 2-11) remains **100% unchanged**.

The only change is:
- ❌ Remove your old `model.save()` and `model.deploy()` cells
- ✅ Replace with new manager cells (12-16)

## Blue-Green Workflow

```
Production (v1) running ────────────────┐
                                        │
Cell 0-1: Backup v1                     │ v1 still serving traffic
Cell 2-11: Train v2                     │
Cell 12-13: Deploy v2 to TEST          │
Cell 14: Test v2                        │
                                        │
        Decision Point                  │
            │                           │
    ┌───────┴────────┐                 │
    │                │                 │
Cell 15:         Cell 16:              │
PROMOTE          ROLLBACK              │
    │                │                 │
    v                v                 │
Production      Production             │
uses v2         stays v1 ──────────────┘
v1 TEST
deleted
```

## First Time Setup

If this is your first time using the manager, add ONE MORE cell before Cell 0:

```python
# FIRST TIME ONLY: Import existing deployment
from recommender_deployment_manager import RecommenderDeploymentManager

manager = RecommenderDeploymentManager()

if manager.get_next_version() == 1:
    manager.import_existing_deployment(
        deployment_id="ocid1.datasciencemodeldeployment.oc1.ap-singapore-1.amaaaaaahxv2vbyapmduolpu3xvaq6q2v2s7le6duh2jeg3xlnxyjxvebxra",
        model_id="ocid1.datasciencemodel.oc1.ap-singapore-1.amaaaaaahxv2vbya4xfaudqcdniewolpqr2obqg6h7nckabrws2qhjqml5kq",
        endpoint="https://modeldeployment.ap-singapore-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.ap-singapore-1.amaaaaaahxv2vbyapmduolpu3xvaq6q2v2s7le6duh2jeg3xlnxyjxvebxra",
        version=1,
        description="Original 26-user model"
    )
    print("✅ Existing deployment imported as v1")
else:
    print("✅ Already initialized")
```

## Benefits of This Approach

1. ✅ **Zero risk** - Your training code is unchanged
2. ✅ **No code duplication** - Use your proven patterns
3. ✅ **Full blue-green** - Test before promoting
4. ✅ **Easy rollback** - One cell to undo
5. ✅ **Automatic versioning** - v1, v2, v3...
6. ✅ **Automatic backups** - Every training backed up
7. ✅ **Same endpoint URL** - No URL changes when promoting

## Testing Checklist

After integration, verify:
- [ ] Cell 0-1: Manager initializes, shows current version
- [ ] Cell 1: Backup completes (if not first run)
- [ ] Cells 2-11: Training works exactly as before
- [ ] Cell 12: Model saves to catalog with TEST label
- [ ] Cell 13: TEST deployment succeeds, different from production
- [ ] Cell 14: Testing works on TEST endpoint
- [ ] Cell 15 OR 16: Promotion or rollback succeeds

## Need Help?

If you have issues:
1. Your training code (Cells 2-11) should work exactly as before
2. If manager cells fail, check `deployment_state.json` exists
3. If first-time import needed, add the import cell

## Files Needed

Upload to `/home/datascience/`:
- `recommender_deployment_manager.py` (the Python module)

That's it! Your existing notebook + 1 file = Blue-green deployment! 🎉
