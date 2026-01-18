# Section 1: Architecture & Design - Implementation Guide

## Overview

Section 1 focuses on finalizing architectural decisions and designing the API structure. Many decisions are already documented in `design.md`, but we need to complete the detailed design work.

## Task Status

### ✅ Already Completed (from design.md)

- **1.1 Backend Framework**: ✅ **Next.js API Routes** (decided)
- **1.5 ADB Connection Method**: ✅ **Wallet-based authentication** (decided and working)

### 📋 Tasks to Complete

#### 1.1 - Finalize Backend Framework Decision
**Status**: ✅ Already decided (Next.js API Routes)
**Action**: Document the decision if not already done

#### 1.2 - Design API Endpoint Structure
**Status**: ⏳ **TODO**
**Action**: Design the specific endpoints needed for KPI #1

**Required Endpoints** (from spec):
- `GET /api/kpi/churn/summary` - Summary metrics (at-risk count, avg risk, LTV at risk)
- `GET /api/kpi/churn/cohorts` - Cohort breakdown with risk scores
- `GET /api/kpi/churn/metrics` - Model confidence, last update
- `GET /api/kpi/churn/chart-data` - Time series data for charts

**Next Steps**:
1. Review existing KPI #1 data structure
2. Design request/response schemas
3. Document endpoint contracts

#### 1.3 - Design Database Schema for OML Dataset Storage
**Status**: ⏳ **TODO**
**Action**: Design tables and views in OML schema

**Required Schema**:
- Dataset tables (customer data, features)
- Feature engineering views
- Model metadata table
- Scoring results table (optional, for caching)

**Next Steps**:
1. Review dataset requirements (from Section 2)
2. Design table structure
3. Create SQL scripts for schema creation

#### 1.4 - Design ML Pipeline Workflow
**Status**: ⏳ **TODO**
**Action**: Design the train/test/deploy workflow

**Pipeline Steps**:
1. Data ingestion → OML schema
2. Feature engineering → Views
3. Model training → XGBoost via OML4Py
4. Model evaluation → Metrics (AUC, precision, recall)
5. Model deployment → Save to OML datastore
6. Model scoring → Batch prediction

**Next Steps**:
1. Create pipeline script structure
2. Design error handling
3. Design model versioning

#### 1.5 - Document ADB Connection Method
**Status**: ✅ **Already documented**
**Action**: Connection method is wallet-based, already working

#### 1.6 - Create API Data Contract Documentation
**Status**: ⏳ **TODO**
**Action**: Document request/response schemas

**Next Steps**:
1. Review KPI #1 frontend data structure
2. Design API response schemas
3. Create TypeScript types
4. Document in OpenAPI/Swagger format (optional)

## Recommended Order

1. **Start with 1.2** (API Endpoint Structure) - This defines what the API needs to provide
2. **Then 1.3** (Database Schema) - This defines where data is stored
3. **Then 1.4** (ML Pipeline) - This defines how models are created
4. **Finally 1.6** (Data Contracts) - This formalizes the API interface

## Quick Start: Task 1.2

To start with Task 1.2, you need to:

1. **Review existing KPI #1 data structure**:
   ```bash
   # Check the frontend code
   cat app/data/synthetic/kpi1-churn-risk.ts
   cat app/lib/types/kpi.ts
   ```

2. **Design API endpoints** based on what KPI #1 needs

3. **Create endpoint specifications** in `openspec/changes/add-churn-model-backend-api/specs/churn-model-api/spec.md`

## Files to Review

- `openspec/changes/add-churn-model-backend-api/design.md` - Architecture decisions
- `openspec/changes/add-churn-model-backend-api/specs/churn-model-api/spec.md` - API spec
- `app/data/synthetic/kpi1-churn-risk.ts` - Current KPI #1 data structure
- `app/lib/types/kpi.ts` - TypeScript types for KPIs

## Next Steps

1. Review the existing KPI #1 data structure
2. Design API endpoints to match frontend needs
3. Create detailed endpoint specifications
4. Proceed to Section 2 (Dataset Acquisition) or Section 3 (ML Pipeline)
