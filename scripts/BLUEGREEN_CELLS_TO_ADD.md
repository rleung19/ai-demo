# Blue-Green Deployment — Cells to ADD to YOUR Notebook

**I am NOT giving you any training code.**  
**You keep 100% of your existing code. You only ADD these 7 cells.**

---

## What You Do

1. Open **your** `Recommender-2.ipynb` (or whatever it’s called).
2. **Add** the 2 cells under “AT THE BEGINNING” (after your `ads.set_auth` / setup, before data extraction).
3. Run your notebook as usual. **Do not remove or change any of your cells.**
4. **Remove** only your `model.save()` and `model.deploy()` cells (or skip running them).
5. **Add** the 5 cells under “AT THE END” and run those.

---

## Files You Need

- `recommender_deployment_manager.py` in `/home/datascience/`
- *(Optional)* `recommender_new_user_fallback.py` in `/home/datascience/` — for new-user recommendations (see below).

**Note (ADS Recommender Operator):** The operator writes to `output_dir` (e.g. `/home/datascience/results`) including `recommendations.csv` and a **report with recommendations for new users**. At train time, `recommendations.csv` is used to build `recommender_dict` and save it to `recommender_model.pkl`. At inference, **`score.py` loads only `recommender_model.pkl`** (not the CSV). Use the **New-user recommendations** section below to also serve new users.

---

## Manual promote option (no TEST deployment) — use when Cell F fails

Use this when automated promote (Cell F) fails (e.g. 400, InvalidConfig) or you prefer not to create a TEST deployment. You skip **Cell D and E**, test the model **locally**, update the prod deployment in **OCI Console**, then **sync state**.

| Step | What to do |
|------|------------|
| **A, B** | Run as usual (init, backup). |
| **C** | Run Cell C to save the new model to the catalog. Note the `model_id` it prints. |
| **Local test** | In a new cell, run e.g. `model.predict({"user_id": "100773", "top_k": 5})` to confirm the model works. Adjust `user_id` to match your data. |
| **OCI Console** | **Data Science → Model Deployments →** your prod deployment → **Edit** → set **Model** to the new model OCID (`model_id` from C) → **Save**. |
| **State update** | In a new cell, run the following so the manager’s state matches the Console. Use the `model_id` from Cell C and `next_version` from Cell A. |

```python
prod = manager.state["production_deployment"]
manager.repair_production_state(prod["deployment_id"], model_id, prod["endpoint"], version=next_version)
print(manager.get_deployment_summary())
print(f"v{next_version} is now in PRODUCTION")
```

*State update tells the manager: production is still the same deployment and URL, but it’s now serving the new model and version, so `current_version` and the next retrain are correct.*

Skip **Cell D, E, F**. You do **not** run `cleanup_test_deployment` (no TEST deployment was created).

---

## AT THE BEGINNING

*Add these 2 cells after your setup/auth, before you run any data extraction.*

### Cell A — Manager init

```python
import sys
sys.path.append('/home/datascience')
from recommender_deployment_manager import RecommenderDeploymentManager

manager = RecommenderDeploymentManager(
    project_name="Product Recommender",
    backup_root="/home/datascience/backups",
    artifact_dir="/home/datascience/recommender_model_artifact",
    results_dir="/home/datascience/results"
)

print(manager.get_deployment_summary())

next_version = manager.get_next_version()
current_version = manager.state['current_version']
print(f"\nNext version to be trained: v{next_version}")
```

### Cell B — Backup

```python
# Use state so this stays correct after a repair (avoids stale current_version)
current_version = manager.state['current_version']
if current_version > 0:
    backup_dir = manager.backup_current_artifacts(version=current_version)
    print(f"Backed up v{current_version} to: {backup_dir}")
else:
    print("No previous version to backup (first deployment)")
```

---

## AT THE END

*Add these 5 cells after your model preparation. Remove or do not run your `model.save()` and `model.deploy()`.*

These cells assume your notebook already has: `model`, `users_df`, `interactions_df`, `recommendations_df`, and that `manager`, `next_version`, `current_version` were set by Cell A and B.

### Cell C — Save to catalog (TEST)

```python
model_id = manager.save_new_model(
    model=model,
    version=next_version,
    num_users=len(users_df),
    num_products=interactions_df['PRODUCT_ID'].nunique(),
    is_test=True
)
print(f"Model v{next_version} saved: {model_id}")
```

*If your `interactions_df` uses a different column name for product (e.g. `product_id`), use that instead of `'PRODUCT_ID'`.*

---

*If you are using the **manual promote** option above, stop after Cell C and the local test, then do the OCI Console edit and state update. The cells below (D, E, F) are for the **automated** path (deploy to TEST, then promote).*

### Cell D — Deploy to TEST

```python
test_deployment = manager.deploy_model(
    model=model,
    model_id=model_id,
    version=next_version,
    is_test=True,
    instance_shape="VM.Standard.E4.Flex",
    ocpus=1,
    memory_gb=16
)
print(f"TEST URL: {test_deployment.url}")
print(manager.get_deployment_summary())
```

### Cell E — Test the deployment

```python
import json

# Use a user_id that exists in your recommendations
result = test_deployment.predict({"user_id": "100773", "top_k": 5})
print(json.dumps(result, indent=2))

result = test_deployment.predict({"user_id": "unknown_123", "top_k": 5})
print(json.dumps(result, indent=2))
```

### Cell F — Promote to production (run only if tests are OK)

```python
manager.promote_to_production()
print(manager.get_deployment_summary())
print(f"v{next_version} is now in PRODUCTION")
```

*Promote tries OCI client update first, then verifies in OCI that the model actually changed. Only if verify passes does it delete the test deployment and update state. If promote raises an OCI/ADS error (e.g. 400 CannotParseRequest), production was **not** changed; fix the cause and re-run the promote cell. After a successful promote, confirm in OCI Console that the deployment’s model is the new one.*

### Cell G — Rollback (run only if you do NOT want to promote)

```python
manager.cleanup_test_deployment()
if current_version > 0:
    manager.rollback_artifacts(version=current_version)
print(manager.get_deployment_summary())
print(f"Rolled back to v{current_version}")
```

---

## New-user recommendations (optional)

Use this so **score.py** can return recommendations for **new users** (user_id not in training) instead of an empty list. The ADS operator may write a report with new-user recommendations; we also support a **popularity fallback** from `recommendations.csv` if that report is missing or in a different format.

### 1. Build and save the fallback

In the **same cell** where you save `recommender_model.pkl` to `artifact_dir`, **after** `os.makedirs(artifact_dir, exist_ok=True)` (or after `shutil.rmtree` + `makedirs`) and **before or after** `joblib.dump(recommender_dict, ...)`, add:

**Option A — using the helper** (place `recommender_new_user_fallback.py` in `/home/datascience/`):

```python
import sys
sys.path.append('/home/datascience')
from recommender_new_user_fallback import build_and_save_new_user_fallback

results_dir = "/home/datascience/results"   # or getattr(manager, 'results_dir', '/home/datascience/results')
artifact_dir = "/home/datascience/recommender_model_artifact"

fallback = build_and_save_new_user_fallback(
    results_dir, artifact_dir, recommendations_df,
    # new_user_csv_path="/home/datascience/results/new_user_recommendations.csv",  # if operator uses another name
)
print(f"New-user fallback: {len(fallback)} items (from operator report or popularity)")
```

**Option B — inline** (no extra file; uses only `pandas`, `joblib`, `os`):

```python
import os
import joblib
import pandas as pd

results_dir = "/home/datascience/results"
artifact_dir = "/home/datascience/recommender_model_artifact"

def _infer(df, *names):
    for c in names:
        if c in df.columns: return c
    return None

fallback = []
for fn in ("new_user_recommendations.csv", "cold_start_recommendations.csv", "recommendations_new_users.csv", "new_users.csv"):
    p = os.path.join(results_dir, fn)
    if os.path.isfile(p):
        df = pd.read_csv(p)
        ic, sc = _infer(df, "PRODUCT_ID", "product_id", "item_id", "movie_id"), _infer(df, "RATING", "rating", "score", "Score")
        if ic and sc:
            if "user_id" in df.columns or "USER_ID" in df.columns:
                agg = df.groupby(ic)[sc].mean().sort_values(ascending=False).head(200)
                fallback = [(str(k), float(v)) for k, v in agg.items()]
            else:
                tmp = df[[ic, sc]].drop_duplicates().sort_values(sc, ascending=False).head(200)
                fallback = [(str(row[ic]), float(row[sc])) for _, row in tmp.iterrows()]
            break
if not fallback and recommendations_df is not None and len(recommendations_df) > 0:
    ic = _infer(recommendations_df, "PRODUCT_ID", "product_id", "item_id", "movie_id")
    sc = _infer(recommendations_df, "RATING", "rating", "score", "Score")
    if ic and sc:
        agg = recommendations_df.groupby(ic)[sc].mean().sort_values(ascending=False).head(200)
        fallback = [(str(k), float(v)) for k, v in agg.items()]

joblib.dump(fallback, os.path.join(artifact_dir, "new_user_fallback.pkl"))
print(f"New-user fallback: {len(fallback)} items")
```

If the operator’s new-user report uses a **different path**, set `new_user_csv_path=...` in Option A, or in Option B add that path as the first file to try in the loop.

### 2. Use this score.py

**Overwrite** your `score.py` in the artifact with the version below. It loads `recommender_model.pkl` and `new_user_fallback.pkl` (if present). For unknown `user_id` it returns `new_user_fallback[:top_k]` with message `"Recommendations for new user (popular items)"`.

- If your main model stores `(product_id, rating)` tuples, the script supports that.
- If it stores `{"product_id", "score"}` dicts, it passes them through. The new-user branch returns `{"product_id", "score"}`; if your API expects `"rating"`, change `"score"` to `"rating"` in the `format_fallback` line.

```python
import json
import os
import joblib

_MODEL = None
_NEW_USER_FALLBACK = None

def load_model(model_file_name="recommender_model.pkl"):
    global _MODEL, _NEW_USER_FALLBACK
    model_dir = os.path.dirname(os.path.realpath(__file__))
    _MODEL = joblib.load(os.path.join(model_dir, model_file_name))
    fb_path = os.path.join(model_dir, "new_user_fallback.pkl")
    _NEW_USER_FALLBACK = joblib.load(fb_path) if os.path.isfile(fb_path) else []
    return _MODEL

def predict(data, model=None):
    global _MODEL, _NEW_USER_FALLBACK
    if model is None:
        if _MODEL is None:
            load_model()
        model = _MODEL
    if _NEW_USER_FALLBACK is None:
        d = os.path.dirname(os.path.realpath(__file__))
        _NEW_USER_FALLBACK = joblib.load(os.path.join(d, "new_user_fallback.pkl")) if os.path.isfile(os.path.join(d, "new_user_fallback.pkl")) else []
    fallback = _NEW_USER_FALLBACK

    try:
        if isinstance(data, str):
            payload = json.loads(data)
        else:
            payload = data
        if isinstance(payload, list) and len(payload) > 0:
            payload = payload[0]
        user_id = str(payload.get("user_id", ""))
        top_k = int(payload.get("top_k", 10))

        if user_id in model:
            recs = model[user_id][:top_k]
            if recs and isinstance(recs[0], (list, tuple)):
                recommendations = [{"product_id": str(p), "rating": float(r)} for p, r in recs]
            else:
                recommendations = recs
            return {"user_id": user_id, "recommendations": recommendations, "message": "Success" if recommendations else "No recommendations found"}
        else:
            recs = fallback[:top_k]
            recommendations = [{"product_id": str(p), "score": float(s)} for p, s in recs]
            return {"user_id": user_id, "recommendations": recommendations, "message": "Recommendations for new user (popular items)" if recommendations else "No recommendations found"}
    except Exception as e:
        return {"error": str(e)}
```

---

## Repairing state after a failed promote

If a **buggy** promote already overwrote state (production shows the test deployment’s endpoint, or "v2 in production" but the OCI update failed), run a one-off repair **after** re-running Cell A (so `manager` exists).

### Option 1 — From a backup (e.g. v1)

If you have a backup for the version that is actually in production:

```python
manager.repair_production_state_from_backup(version=1)
```

### Option 2 — Manual (real prod deployment_id, model_id, endpoint)

If you don’t have a usable backup, get the **real** production deployment OCID, model OCID, and URL from OCI Console (Model Deployment → your prod → Configuration and URL), then:

```python
manager.repair_production_state(
    deployment_id="ocid1.datasciencemodeldeployment.oc1.ap-singapore-1.amaaaaaa...vebxra",  # real prod, NOT ...jwqa
    model_id="ocid1.datasciencemodel.oc1.ap-singapore-1.amaaaaaa...",   # v1 model actually in prod
    endpoint="https://modeldeployment.ap-singapore-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment...",
    version=1
)
```

After repair, `get_deployment_summary()` should show PRODUCTION with the correct endpoint and `current_version` 1.

**Re-run Cell A** after repair so `current_version` and `next_version` are correct. Then run Cell B (it reads from `manager.state`, so the backup will be labeled v1). You can then retrain and run the blue‑green flow from Cell C onward.

If you already ran Cell B before re-running Cell A, the backup may be labeled v2 — that’s a one-off mismatch; re-run Cell A and continue. The v2 backup’s metadata has the correct `production_deployment`; for rollback to v1 you’d need an older v1 backup.

---

## Summary

- **Your notebook:** all your training, data, operator, model prep — unchanged.
- **You add:**  
  - 2 cells at the beginning (init + backup).  
  - 5 cells at the end (save, deploy, test, promote/rollback).  
- **You remove/skip:** only `model.save()` and `model.deploy()`.

**Two promote paths:**
- **Manual promote** (no Cell D/E/F): save to catalog (C), local test, OCI Console edit, state update. Use when Cell F fails or you prefer not to create a TEST deployment.
- **Automated** (Cells D→E→F): deploy to TEST, test on endpoint, promote. Use when Cell F works.

No training code is provided or changed here. Only these 7 deployment cells.
