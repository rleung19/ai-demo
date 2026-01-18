# Implementation Tasks

## 0. Prerequisites & Setup
- [ ] 0.1 Verify Oracle ADB Serverless access and OML enabled
- [ ] 0.2 Download and configure ADB wallet
- [ ] 0.3 Set up Python environment (3.8+) with OML4Py
- [ ] 0.4 Set up Node.js environment with required packages
- [ ] 0.5 Create OML schema if not exists
- [ ] 0.6 Test ADB connection from both Python and Node.js
- [ ] 0.7 Set up environment variables for ADB connection (wallet path, credentials)
- [ ] 0.8 Create `.env.example` file with required variables
- [ ] 0.9 Document wallet download and setup process

## 1. Architecture & Design
- [ ] 1.1 Decide backend framework (Express.js vs FastAPI vs Next.js API routes)
- [ ] 1.2 Design API endpoint structure and data contracts
- [ ] 1.3 Design database schema for OML dataset storage
- [ ] 1.4 Design ML pipeline workflow (train/test/deploy)
- [ ] 1.5 Document ADB connection method (wallet vs connection string)
- [ ] 1.6 Create API data contract documentation (request/response schemas)

## 2. Dataset Acquisition & Preparation
- [ ] 2.1 Research and identify proven churn datasets (Kaggle or academic sources)
- [ ] 2.2 Evaluate dataset quality (size, features, churn rate, data quality)
- [ ] 2.3 Download and prepare dataset locally
- [ ] 2.4 Create data mapping document (source → OML schema)
- [ ] 2.5 Create data ingestion script to load dataset into OML schema
- [ ] 2.6 Validate data loaded correctly (row counts, data types, constraints)
- [ ] 2.7 Create feature engineering views in OML schema
- [ ] 2.8 Validate dataset produces reasonable model performance (AUC > 0.70 on validation set)

## 3. ML Pipeline Development
- [ ] 3.1 Create Python script for ADB connection (OML4Py)
- [ ] 3.2 Implement data loading and preprocessing
- [ ] 3.3 Implement feature selection and validation
- [ ] 3.4 Implement model training (XGBoost via OML4Py, consider AutoML)
- [ ] 3.5 Implement model evaluation (metrics: AUC, precision, recall, F1)
- [ ] 3.6 Implement threshold optimization for binary classification
- [ ] 3.7 Implement model saving to OML datastore with versioning
- [ ] 3.8 Implement model scoring (batch prediction for all customers)
- [ ] 3.9 Create automated pipeline script (train/test/deploy workflow)
- [ ] 3.10 Add model versioning and performance tracking
- [ ] 3.11 Create model comparison report (XGBoost vs AutoML if both tested)
- [ ] 3.12 Test pipeline end-to-end (data → model → predictions)

## 4. Backend API Development
- [ ] 4.1 Set up Next.js API routes structure
- [ ] 4.2 Implement ADB connection utilities with connection pooling
- [ ] 4.3 Create health check endpoint (`GET /api/health`)
- [ ] 4.4 Create API endpoint: `GET /api/kpi/churn/summary` (at-risk count, avg risk, LTV at risk)
- [ ] 4.5 Create API endpoint: `GET /api/kpi/churn/cohorts` (cohort breakdown with risk scores)
- [ ] 4.6 Create API endpoint: `GET /api/kpi/churn/metrics` (model confidence, last update)
- [ ] 4.7 Create API endpoint: `GET /api/kpi/churn/chart-data` (time series data for charts)
- [ ] 4.8 Implement request validation and input sanitization
- [ ] 4.9 Implement error handling and logging
- [ ] 4.10 Add API response caching (optional, for performance)
- [ ] 4.11 Create API documentation (OpenAPI/Swagger or markdown)

## 5. Frontend Integration
- [ ] 5.1 Create API client utility (`app/lib/api/churn-api.ts`)
- [ ] 5.2 Update `app/data/kpis/index.ts` to fetch from API with fallback to static data
- [ ] 5.3 Update KPI #1 card to use real-time data
- [ ] 5.4 Update KPI #1 detail modal to use API data
- [ ] 5.5 Add loading states and error handling
- [ ] 5.6 Add retry logic for failed API calls
- [ ] 5.7 Implement request debouncing for chart data
- [ ] 5.8 Add visual indicator when using fallback data
- [ ] 5.9 Test API integration with backend

## 6. Testing & Validation
- [ ] 6.1 Test ML pipeline end-to-end (data → model → predictions)
- [ ] 6.2 Test API endpoints with real model data
- [ ] 6.3 Test API with no model available (fallback scenario)
- [ ] 6.4 Test API with slow database connection (timeout handling)
- [ ] 6.5 Test frontend integration (API calls, error handling, fallbacks)
- [ ] 6.6 Validate model performance meets targets (AUC > 0.70)
- [ ] 6.7 Test with different time periods and filters
- [ ] 6.8 Test model retraining workflow
- [ ] 6.9 Load testing for API endpoints (optional but useful)

## 7. Documentation
- [ ] 7.1 Document API endpoints (request/response formats)
- [ ] 7.2 Document ML pipeline usage and configuration
- [ ] 7.3 Document dataset source and preparation steps
- [ ] 7.4 Update README with setup instructions
- [ ] 7.5 Document ADB wallet setup and connection process
- [ ] 7.6 Create troubleshooting guide for common issues
