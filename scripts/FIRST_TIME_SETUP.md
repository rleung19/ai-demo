# First Time Setup Guide

## Problem: Importing Your Existing Deployment

When you first use the deployment management system, it doesn't know about your existing production model. Without importing it, the system will:

- ❌ Think you have no deployments (when you actually do!)
- ❌ Skip backing up your current model
- ❌ Potentially overwrite your production artifacts
- ❌ Start versioning from v1 (when you might want v2)

## Solution: Import Your Existing Deployment

The updated system now includes an **import cell** that registers your existing deployment so it can be properly tracked, backed up, and managed.

## Step-by-Step First Time Setup

### 1. Find Your Current Deployment Info

Go to **OCI Console → Data Science → Model Deployments** and find your production deployment.

Copy these 3 values:

1. **Deployment OCID** - Example:
   ```
   ocid1.datasciencemodeldeployment.oc1.ap-singapore-1.amaaaaaahxv2vbyapmduolpu3xvaq6q2v2s7le6duh2jeg3xlnxyjxvebxra
   ```

2. **Model OCID** - Click into the deployment, then click the model link. Example:
   ```
   ocid1.datasciencemodel.oc1.ap-singapore-1.amaaaaaahxv2vbya4xfaudqcdniewolpqr2obqg6h7nckabrws2qhjqml5kq
   ```

3. **Endpoint URL** - Example:
   ```
   https://modeldeployment.ap-singapore-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.ap-singapore-1.amaaaaaahxv2vbyapmduolpu3xvaq6q2v2s7le6duh2jeg3xlnxyjxvebxra
   ```

### 2. Upload Files to Data Science Notebook

Upload these files to `/home/datascience/`:

- `recommender_deployment_manager.py`
- `Recommender-Retrain-Template-v2.ipynb` (use the v2 version!)

### 3. Update Cell 2 in the Notebook

Open `Recommender-Retrain-Template-v2.ipynb` and find **Cell 2**.

Update these three lines with your actual values:

```python
# TODO: Update these with your actual production deployment details
EXISTING_DEPLOYMENT_ID = "ocid1.datasciencemodeldeployment.oc1..."  # ⬅️ YOUR DEPLOYMENT OCID
EXISTING_MODEL_ID = "ocid1.datasciencemodel.oc1..."                 # ⬅️ YOUR MODEL OCID
EXISTING_ENDPOINT = "https://modeldeployment.ap-singapore-1..."     # ⬅️ YOUR ENDPOINT URL
```

### 4. Run the Notebook

**First time:**
- Run **Cell 0** (setup)
- Run **Cell 1** (initialize manager)
  - You'll see: "Next version to be trained: v1"
  - This means you need to import!
- Run **Cell 2** (import existing deployment) ⭐ **IMPORTANT**
  - This registers your current model as v1
  - You'll now see: "Next training will create v2"
- Continue with **Cells 3-12** as normal

**Second time onwards:**
- Run **Cell 0** (setup)
- Run **Cell 1** (initialize manager)
  - You'll see: "Next version to be trained: v2" (or v3, v4...)
- **Cell 2 will automatically skip** (already imported!)
- Continue with **Cells 3-12** as normal

## What Happens When You Import

When you run Cell 2, the system:

1. ✅ Registers your existing deployment as **v1**
2. ✅ Saves the deployment info to state file
3. ✅ Sets next version to **v2**
4. ✅ Ensures your v1 artifacts can be backed up before retraining

## Cell 2 Output (Expected)

### First Time (Import Required):

```
🔍 First time setup detected!

Please provide your existing deployment details:
(You can find these in OCI Console → Data Science → Model Deployments)

📥 Importing existing deployment as v1...
  ✓ Imported v1 as current production
  ✓ Model: ocid1.datasciencemodel.oc1.ap-singapore-1.amaaaaaahxv2vbya...
  ✓ Endpoint: https://modeldeployment.ap-singapore-1.oci.customer-oci.com/...

✅ Next retraining will create v2

✅ Import complete! Next training will create v2
```

### Subsequent Runs (Already Imported):

```
✅ Deployment tracking already initialized (next version: v2)
   Skipping import...
```

## Verification

After running Cell 2, run Cell 1 again to verify:

```python
# Re-run Cell 1 to see updated status
print(manager.get_deployment_summary())
```

You should now see:

```
============================================================
🎯 Product Recommender - Deployment Status
============================================================

✅ PRODUCTION (v1)
   Model: ocid1.datasciencemodel.oc1...
   Endpoint: https://modeldeployment.ap-singapore-1...
   Deployed: 2026-01-25T10:30:00

🧪 TEST: No test deployment

📊 Current Version: v1
📦 Total Deployments: 1
============================================================

🎯 Next version to be trained: v2
```

Perfect! Now your existing deployment is tracked and protected.

## Troubleshooting

### Issue: Cell 2 says "already initialized" but I haven't imported

**Solution:** The state file already exists. To reset:

```python
# In a new cell, delete the state file and restart
import os
state_file = "/home/datascience/backups/deployment_state.json"
if os.path.exists(state_file):
    os.remove(state_file)
    print("✅ State file deleted. Re-run Cell 1 and Cell 2.")
```

### Issue: I ran the notebook without importing first

**Solution:** Import manually:

```python
# In a new cell
from recommender_deployment_manager import RecommenderDeploymentManager

manager = RecommenderDeploymentManager()

manager.import_existing_deployment(
    deployment_id="ocid1.datasciencemodeldeployment.oc1...",
    model_id="ocid1.datasciencemodel.oc1...",
    endpoint="https://modeldeployment.ap-singapore-1...",
    version=1,
    description="Original model (imported after training)"
)
```

### Issue: Wrong OCIDs imported

**Solution:** Edit the state file directly:

```python
# Read and edit state
import json
state_file = "/home/datascience/backups/deployment_state.json"

with open(state_file, 'r') as f:
    state = json.load(f)

print(json.dumps(state, indent=2))

# Update values as needed
state["production_deployment"]["model_id"] = "correct_ocid..."
state["production_deployment"]["endpoint"] = "correct_url..."

# Save back
with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)

print("✅ State file updated")
```

## Summary: Use Template v2

Always use **`Recommender-Retrain-Template-v2.ipynb`** which includes:

- ✅ Cell 2: Automatic import detection
- ✅ Smart version tracking
- ✅ Protection for existing deployments
- ✅ Backup before every retrain

The old template (`Recommender-Retrain-Template.ipynb`) doesn't have the import feature and should not be used if you have existing deployments.
