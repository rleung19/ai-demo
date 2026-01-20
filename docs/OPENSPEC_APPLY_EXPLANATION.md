# What is "openspec apply"?

## Short Answer

**"openspec apply"** is a **conceptual term**, not a literal CLI command. The actual command is **`openspec archive`**.

## Detailed Explanation

### The Confusion

You may have seen "openspec apply" mentioned in:
- Documentation that uses it as a conceptual term
- UI interfaces that describe the workflow
- Discussions about "applying spec deltas"

But when you check the CLI, there's no `openspec apply` command - only `openspec archive`.

### What "Apply" Actually Means

"Apply" refers to the process of:
1. **Archiving the change** - Moving from `openspec/changes/<change-id>/` to `openspec/changes/archive/YYYY-MM-DD-<change-id>/`
2. **Applying spec deltas** - Merging the delta specs (ADDED/MODIFIED/REMOVED) into the canonical `openspec/specs/` directory
3. **Making specs reflect reality** - Updating the "source of truth" specs to match what was actually built

### The Actual Command

```bash
# This is what you run (not "openspec apply")
openspec archive add-churn-model-backend-api --yes
```

This command:
- Moves the change folder to archive
- Merges spec deltas into `openspec/specs/`
- Updates the canonical specs to reflect implemented changes

### Why the Terminology?

The term "apply" makes sense conceptually:
- You're **applying** the proposed changes to the live specs
- You're **applying** the deltas to update the canonical requirements
- You're **applying** the implementation to the project's source of truth

But the CLI command is called `archive` because:
- It archives the completed change
- It's the final step in the workflow
- It marks the change as "done"

## Workflow Summary

```
Stage 1: Proposal
  └─ Create proposal in openspec/changes/<id>/

Stage 2: Implementation  
  └─ Build features, mark tasks complete

Stage 3: Archive/Apply  ← This is what "apply" means
  └─ Run: openspec archive <id>
  └─ Moves to archive/
  └─ Updates specs/ with deltas
```

## When to Run Archive

Run `openspec archive` when:
- ✅ All tasks in `tasks.md` are complete
- ✅ Code is implemented and tested
- ✅ Changes are deployed (or ready to deploy)
- ✅ You want to update `openspec/specs/` to reflect reality

## Example

```bash
# After completing implementation and testing:
openspec archive add-churn-model-backend-api --yes

# This will:
# 1. Move openspec/changes/add-churn-model-backend-api/ 
#    → openspec/changes/archive/2026-01-18-add-churn-model-backend-api/
# 2. Merge spec deltas into openspec/specs/
# 3. Update canonical specs to match what was built
```

## Summary

| Term | Meaning | Command |
|------|---------|---------|
| **"openspec apply"** | Conceptual term for archiving/applying deltas | N/A (not a command) |
| **`openspec archive`** | Actual CLI command | `openspec archive <change-id>` |

**Bottom line**: If you see "openspec apply" mentioned, it's referring to the `openspec archive` command and the process of applying spec deltas to your live specs.
