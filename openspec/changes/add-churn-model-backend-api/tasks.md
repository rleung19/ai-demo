# Implementation Tasks

## 0. Prerequisites & Setup
- [x] 0.1 Verify Oracle ADB Serverless access and OML enabled
- [x] 0.2 Download and configure ADB wallet
- [x] 0.3 Set up Python environment (3.8+) with OML4Py (also set up for local training)
- [x] 0.4 Set up Node.js environment with required packages
- [x] 0.5 Create OML schema if not exists
- [x] 0.6 Test ADB connection from both Python and Node.js
- [x] 0.7 Set up environment variables for ADB connection (wallet path, credentials)
- [x] 0.8 Create `.env.example` file with required variables
- [x] 0.9 Document wallet download and setup process

## 1. Architecture & Design
- [x] 1.1 Decide backend framework (Next.js API routes - decided)
- [x] 1.2 Design API endpoint structure and data contracts - API_ENDPOINT_DESIGN.md created
- [x] 1.3 Design database schema for OML dataset storage (tables and views created)
- [x] 1.4 Design ML pipeline workflow (train/test/deploy - local training approach)
- [x] 1.5 Document ADB connection method (wallet-based - documented)
- [x] 1.6 Create API data contract documentation (request/response schemas) - API_DATA_CONTRACTS.md created

## 2. Dataset Acquisition & Preparation
- [x] 2.1 Research and identify proven churn datasets (Kaggle: dhairyajeetsingh dataset selected)
- [x] 2.2 Evaluate dataset quality (size, features, churn rate, data quality)
- [x] 2.3 Download and prepare dataset locally (processed and mapped datasets created)
- [x] 2.4 Create data mapping document (source → OML schema) - DATA_MAPPING_DOCUMENT.md
- [x] 2.5 Create data ingestion script to load dataset into OML schema - ingest_churn_data.py
- [x] 2.6 Validate data loaded correctly (row counts, data types, constraints) - validate_churn_data.py
- [x] 2.7 Create feature engineering views in OML schema - create_feature_views.sql
- [x] 2.8 Validate dataset produces reasonable model performance (AUC 0.9190 on validation set) - validate_model_performance.py

## 3. ML Pipeline Development
- [x] 3.1 Create Python script for ADB connection (oracledb for local training)
- [x] 3.2 Implement data loading and preprocessing
- [x] 3.3 Implement feature selection and validation
- [x] 3.4 Implement model training (XGBoost - local training, AUC 0.9269)
- [x] 3.5 Implement model evaluation (metrics: AUC, precision, recall, F1)
- [x] 3.6 Implement threshold optimization for binary classification
- [x] 3.7 Implement model saving (pickle files + metadata)
- [x] 3.8 Implement model scoring (batch prediction for all customers) - local model script created
- [x] 3.9 Create automated pipeline script (train/test/deploy workflow) - updated for local training
- [x] 3.10 Add model versioning and performance tracking - MODEL_REGISTRY table created, training script updated
- [x] 3.11 Create model comparison report (CatBoost, GradientBoosting, RandomForest, AdaBoost tested)
- [x] 3.12 Test pipeline end-to-end (data → model → predictions) - test script created

## 4. Backend API Development
- [x] 4.1 Set up Next.js API routes structure
- [x] 4.2 Implement ADB connection utilities with connection pooling
- [x] 4.3 Create health check endpoint (`GET /api/health`)
- [x] 4.4 Create API endpoint: `GET /api/kpi/churn/summary` (at-risk count, avg risk, LTV at risk)
- [x] 4.5 Create API endpoint: `GET /api/kpi/churn/cohorts` (cohort breakdown with risk scores)
- [x] 4.6 Create API endpoint: `GET /api/kpi/churn/metrics` (model confidence, last update)
- [x] 4.7 Create API endpoint: `GET /api/kpi/churn/chart-data` (time series data for charts)
- [x] 4.8 Implement request validation and input sanitization
- [x] 4.9 Implement error handling and logging
- [x] 4.10 Add API response caching (optional, for performance)
- [x] 4.11 Create API documentation (OpenAPI/Swagger or markdown)

## 5. Frontend Integration
- [x] 5.1 Create API client utility (`app/lib/api/churn-api.ts`)
- [x] 5.2 Update `app/data/kpis/index.ts` to fetch from API with fallback to static data
- [x] 5.3 Update KPI #1 card to use real-time data
- [x] 5.4 Update KPI #1 detail modal to use API data
- [x] 5.5 Add loading states and error handling
- [x] 5.6 Add retry logic for failed API calls
- [x] 5.7 Implement request debouncing for chart data (optional optimization)
- [x] 5.8 Add visual indicator when using fallback data
- [x] 5.9 Test API integration with backend

## 6. Testing & Validation
- [x] 6.1 Test ML pipeline end-to-end (data → model → predictions)
- [x] 6.2 Test API endpoints with real model data
- [ ] 6.3 Test API with no model available (fallback scenario)
- [ ] 6.4 Test API with slow database connection (timeout handling)
- [ ] 6.5 Test frontend integration (API calls, error handling, fallbacks)
- [x] 6.6 Validate model performance meets targets (AUC > 0.70)
- [ ] 6.7 Test with different time periods and filters
- [ ] 6.8 Test model retraining workflow
- [ ] 6.9 Load testing for API endpoints (optional but useful)

## 7. Documentation
- [x] 7.1 Document API endpoints (request/response formats)
- [x] 7.2 Document ML pipeline usage and configuration
- [x] 7.3 Document dataset source and preparation steps
- [x] 7.4 Update README with setup instructions
- [x] 7.5 Document ADB wallet setup and connection process
- [x] 7.6 Create troubleshooting guide for common issues

## 8. OCI Deployment
- [x] 8.1 Create Dockerfile for containerized deployment
- [x] 8.2 Create podman-compose.yml configuration
- [x] 8.3 Configure Oracle Instant Client in Docker image
- [x] 8.4 Set up wallet volume mounting in compose file
- [x] 8.5 Configure environment variables for OCI deployment
- [x] 8.6 Create OCI deployment documentation (README_OCI_VM_PODMAN.md)
- [x] 8.7 Document Oracle Instant Client installation process
- [x] 8.8 Document wallet setup and mounting
- [x] 8.9 Document Caddy reverse proxy configuration
- [x] 8.10 Add troubleshooting section for common deployment issues
- [x] 8.11 Test container build process
- [ ] 8.12 Test deployment on OCI VM (end-to-end)
- [ ] 8.13 Verify Oracle connection from container
- [ ] 8.14 Test API endpoints from deployed container
- [ ] 8.15 Verify Caddy reverse proxy routing
