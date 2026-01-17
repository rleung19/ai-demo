# Churn Analysis Model Development - Summary

## Overview

This directory contains complete workflows for developing customer churn prediction models using Oracle Machine Learning (OML) on Oracle Autonomous Database.

## Files Included

### Documentation
- **`PROPOSAL.md`** - Complete business and technical proposal
- **`README.md`** - Quick start guide and file descriptions
- **`EXECUTION_GUIDE.md`** - Step-by-step execution instructions
- **`SUMMARY.md`** - This file

### Notebook Files
- **`churn_analysis_original.json`** - Original model notebook (JSON format - may need format adjustment for OML Notebooks)
- **`churn_analysis_original.md`** - Original model notebook (Markdown format - easy to copy/paste)
- **`churn_analysis_enhanced.md`** - Enhanced model notebook (Markdown format - easy to copy/paste)

## Quick Start

1. **Read the Proposal**: Start with `PROPOSAL.md` to understand the business context
2. **Choose Your Workflow**: 
   - Start with `churn_analysis_original.md` for baseline model
   - Then try `churn_analysis_enhanced.md` for improved model
3. **Import to OML Notebooks**: 
   - Copy cells from markdown files into OML Notebooks UI
   - Or use JSON file if OML Notebooks supports direct import
4. **Follow Execution Guide**: Use `EXECUTION_GUIDE.md` for troubleshooting

## Model Comparison

### Original Model
- **Features**: 42 original features
- **Performance**: AUC-ROC ~0.52 (baseline)
- **Use Case**: Establish baseline, understand data

### Enhanced Model
- **Features**: 42 original + 17 engineered features + categorical encoding
- **Performance**: TBD (run to compare)
- **Use Case**: Improved predictions with feature engineering

## Key Learnings

1. **Categorical Features Matter**: Excluding them hurt model performance
2. **Feature Engineering**: Interaction features can capture complex relationships
3. **Threshold Optimization**: Default 0.5 is not optimal for imbalanced data
4. **OML4Py API**: Specific patterns required (e.g., `oml.sync(view=...)`, `oml.xgb('classification')`)

## Next Steps

1. **Hyperparameter Tuning**: Optimize XGBoost parameters
2. **Alternative Algorithms**: Try Random Forest, GLM
3. **Churn Definition**: Validate with actual churn data
4. **Production Deployment**: Integrate with frontend API

## Support

Refer to individual markdown files for detailed code and explanations.
