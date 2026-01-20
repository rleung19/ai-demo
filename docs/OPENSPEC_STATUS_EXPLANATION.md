# OpenSpec Status and Script Execution - Explanation

## Current Status: **Stage 2 - Implementation Phase**

### OpenSpec Workflow Stages

According to OpenSpec, there are **3 stages**:

1. **Stage 1: Creating Changes (Proposal)** ✅ COMPLETE
   - Location: `openspec/changes/add-churn-model-backend-api/`
   - Files: `proposal.md`, `design.md`, `tasks.md`, `specs/`
   - Status: Proposal created and approved (we started implementing)

2. **Stage 2: Implementing Changes** ✅ IN PROGRESS
   - Location: Code in `scripts/`, `sql/`, `docs/`
   - Status: **We are here** - Scripts created, but need to be run/tested
   - Tasks: All Task 3 items marked complete in `tasks.md`

3. **Stage 3: Archiving Changes** ⏳ NOT YET
   - Command: `openspec archive add-churn-model-backend-api`
   - Action: Moves `changes/` → `changes/archive/YYYY-MM-DD-add-churn-model-backend-api/`
   - Updates: `specs/` directory with final requirements
   - When: After deployment and verification

## Script Execution Status

### ✅ Scripts Created (Implementation Complete)
All scripts have been **created** but **NOT YET RUN/TESTED**:

1. **Database Setup Scripts**:
   - `scripts/create_model_registry_table.py` - Creates MODEL_REGISTRY table
   - `sql/create_model_registry_table.sql` - Table schema
   - **Status**: Created, needs to be run

2. **Training Scripts**:
   - `scripts/local/train_churn_model_local.py` - Trains model
   - **Status**: Created, needs to be run

3. **Scoring Scripts**:
   - `scripts/local/score_churn_model_local.py` - Scores users
   - **Status**: Created, needs to be run

4. **Testing Scripts**:
   - `scripts/local/test_pipeline_end_to_end.py` - End-to-end test
   - **Status**: Created, needs to be run

5. **Pipeline Scripts**:
   - `scripts/local/ml_pipeline.py` - Complete pipeline
   - **Status**: Created, needs to be run

### ⏳ Next Steps: Run and Test

**You need to run these scripts in order**:

```bash
# 1. Create model registry table (one-time setup)
python scripts/create_model_registry_table.py

# 2. Test end-to-end (this will train, score, and verify)
python scripts/local/test_pipeline_end_to_end.py

# OR run individual steps:
# 2a. Train model
python scripts/local/train_churn_model_local.py

# 2b. Score users
python scripts/local/score_churn_model_local.py
```

## OpenSpec Apply vs Archive

### "Apply" is a Conceptual Term

**"openspec apply"** is sometimes used in documentation/UI to refer to the **archiving process** - it means "applying the spec deltas to your live specs". However, the **actual CLI command** is:

- **`openspec archive`** - The command that applies changes and archives the proposal

### What "Apply" Means

When people say "openspec apply", they're referring to:
- **Archiving the change** (moving from `changes/` to `changes/archive/`)
- **Applying spec deltas** (merging changes into `openspec/specs/`)
- **Making specs reflect reality** (updating canonical specs with implemented changes)

The actual command to do this is:
```bash
openspec archive <change-id> [--yes]
```

### ✅ What You Need to Do

1. **Complete Implementation** (Current Stage):
   - ✅ Scripts created
   - ⏳ **Run scripts and verify they work**
   - ⏳ **Test end-to-end pipeline**
   - ⏳ **Verify predictions in database**

2. **After Testing Passes**:
   - Update `tasks.md` if needed (already marked complete)
   - Verify all requirements met
   - **Then** run: `openspec archive add-churn-model-backend-api`

3. **Archive Command**:
   ```bash
   openspec archive add-churn-model-backend-api --yes
   ```
   - Moves change to `archive/` directory
   - Updates `specs/` with final requirements
   - Marks change as complete

## Summary

| Aspect | Status | Action Needed |
|--------|--------|---------------|
| **OpenSpec Stage** | Stage 2 (Implementation) | Continue implementation |
| **Scripts Created** | ✅ Yes | None |
| **Scripts Run/Tested** | ❌ No | **Run and test scripts** |
| **OpenSpec Apply** | ⚠️ Conceptual term | Use `openspec archive` command |
| **OpenSpec Archive** | ⏳ Not yet | After testing passes |

## Recommended Next Steps

1. **Run Setup**:
   ```bash
   python scripts/create_model_registry_table.py
   ```

2. **Run End-to-End Test**:
   ```bash
   python scripts/local/test_pipeline_end_to_end.py
   ```
   This will:
   - Verify data availability
   - Train a model
   - Score users
   - Verify predictions in database
   - Check model registry

3. **If Tests Pass**:
   - All Task 3 work is complete
   - Move to Task 4 (Backend API Development)
   - Archive OpenSpec change after Task 4-6 complete

4. **If Tests Fail**:
   - Fix issues
   - Re-run tests
   - Continue until all pass

## Important Notes

- **Scripts are ready but untested** - You need to run them
- **We're still in implementation phase** - Not ready to archive yet
- **No `openspec-apply`** - Only `openspec archive` after completion
- **Archive after full deployment** - Not just after Task 3, but after all tasks (3-6) are complete
