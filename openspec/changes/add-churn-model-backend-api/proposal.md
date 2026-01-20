# Change: Add Churn Model Backend API

## Why
KPI #1 (Churn Risk Score) currently displays static synthetic data. To demonstrate real AI/ML capabilities, we need a production-ready backend API that connects to Oracle ADB, trains a churn prediction model, and serves live predictions to the dashboard. The current demo data in ADMIN schema produces low AUC models, so we need better datasets and an automated ML pipeline.

## What Changes
- **New Backend API Server**: REST API server connecting to Oracle Autonomous Database Serverless
- **Dataset Acquisition**: Identify and ingest proven churn datasets (Kaggle or simulated) into OML schema
- **Automated ML Pipeline**: Python-based workflow to train, test, and deploy churn models using OML4Py
- **REST API Endpoints**: Endpoints serving KPI #1 metrics (at-risk customers, risk scores, cohort breakdown, LTV at risk)
- **Frontend Integration**: Replace static synthetic data with API calls to backend
- **Model Management**: Model versioning, performance tracking, and deployment automation

## Impact
- **New Capability**: `churn-model-api` - Backend API for churn model predictions
- **Modified Capability**: `kpi-dashboard` - Connect KPI #1 to real API instead of static data
- **New Code**: 
  - Backend server (Express.js/FastAPI/Next.js API routes)
  - ML pipeline scripts (Python with OML4Py)
  - API route handlers
  - Database connection utilities
- **Modified Code**:
  - `app/data/kpis/index.ts` - Replace static data with API calls
  - `app/data/synthetic/kpi1-churn-risk.ts` - Keep as fallback
  - `app/page.tsx` - Add API integration
- **New Dependencies**: Backend framework, Oracle database client, OML4Py
