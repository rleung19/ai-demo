# Design: Churn Model Backend API

## Context
The AI workshop demo needs a production-ready churn prediction system. Currently, KPI #1 displays static synthetic data. We need to connect to Oracle ADB Serverless, train real ML models, and serve predictions via REST API. The existing demo data in ADMIN schema produces low-quality models (AUC ~0.50), so we need better datasets.

**Stakeholders**: Workshop participants, demo audience
**Constraints**: 
- Must work with Oracle ADB Serverless
- Must use OML4Py for model training
- Must integrate with existing Next.js frontend
- Should be demo-ready (fast setup, clear documentation)

## Goals / Non-Goals

### Goals
- Real-time churn predictions from trained ML model
- REST API serving KPI #1 dashboard data
- Automated ML pipeline (train/test/deploy)
- High-quality dataset producing AUC > 0.70
- Seamless frontend integration with fallback to static data

### Non-Goals
- Real-time model retraining (batch is sufficient)
- Multi-tenant support (single demo instance)
- Advanced authentication (demo environment)
- Model A/B testing (single model version)
- Production-grade monitoring/alerting (demo scope)

## Decisions

### Decision: Backend Framework
**Chosen**: Next.js API Routes
**Rationale**: 
- Already using Next.js for frontend
- No additional server infrastructure needed
- Shared TypeScript types between frontend/backend
- Simpler deployment (single application)
- Good enough performance for demo

**Alternatives Considered**:
- Express.js: Would require separate server, more infrastructure
- FastAPI: Python-based, but frontend is TypeScript/Next.js
- Separate Python service: More complex deployment

### Decision: Dataset Source
**Chosen**: Kaggle churn dataset (to be identified) OR simulated data with proper correlations
**Rationale**:
- Kaggle datasets are proven and well-documented
- Simulated data allows full control but requires careful engineering
- Will evaluate both options and choose best performing

**Alternatives Considered**:
- Use existing ADMIN schema data: Rejected (low AUC, too random)
- Public academic datasets: Considered, but Kaggle is more accessible

### Decision: ADB Connection Method
**Chosen**: Wallet-based authentication (standard for ADB Serverless)
**Rationale**:
- Most secure and standard approach for ADB
- Supports both OML4Py (Python) and Node.js (API server)
- Well-documented in Oracle documentation

**Alternatives Considered**:
- Connection string with credentials: Less secure, not recommended for ADB

### Decision: Model Algorithm
**Chosen**: XGBoost via OML4Py (primary), AutoML as fallback
**Rationale**:
- XGBoost is proven for churn prediction
- OML4Py provides native XGBoost support
- AutoML can be used if XGBoost underperforms
- Fast training suitable for demo

**Alternatives Considered**:
- Neural Networks: Overkill for this use case, slower training
- Logistic Regression: Simpler but typically lower performance

### Decision: Model Deployment
**Chosen**: OML Datastore + Direct SQL/OML4Py scoring in API
**Rationale**:
- OML datastore is standard for OML models
- API can load model and score on-demand
- No need for separate model serving infrastructure
- Sufficient for demo scale

**Alternatives Considered**:
- OML Services REST API: More complex setup, requires OML Services configuration
- Separate model serving service: Overkill for demo

### Decision: API Data Structure
**Chosen**: Match existing KPI #1 data structure
**Rationale**:
- Minimal frontend changes required
- Backward compatible with existing static data
- Clear contract between frontend and backend

## Architecture

```
┌─────────────────┐
│  Next.js App   │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼─────────────────┐
│  Next.js API Routes     │
│  /api/kpi/churn/*       │
└────────┬─────────────────┘
         │
         │ OML4Py / SQL
         │
┌────────▼─────────────────┐
│  Oracle ADB Serverless  │
│  - OML Schema           │
│    - Dataset tables     │
│    - Feature views      │
│    - Model datastore    │
│  - ADMIN Schema         │
│    - (existing demo)    │
└─────────────────────────┘

┌─────────────────────────┐
│  ML Pipeline (Python)   │
│  - Data ingestion       │
│  - Feature engineering  │
│  - Model training       │
│  - Model evaluation     │
│  - Model deployment     │
└─────────────────────────┘
```

## Data Flow

1. **Training Pipeline**:
   - Load dataset → OML schema tables
   - Create feature views
   - Train XGBoost model via OML4Py
   - Evaluate and save to OML datastore

2. **API Request Flow**:
   - Frontend requests `/api/kpi/churn/summary`
   - API loads model from OML datastore
   - API scores current customers
   - API aggregates results (cohorts, metrics)
   - API returns JSON matching frontend contract

3. **Frontend Display**:
   - KPI card shows summary metrics
   - Detail modal shows full breakdown
   - Charts render from API data

## Risks / Trade-offs

### Risk: Dataset Quality
**Mitigation**: 
- Evaluate multiple datasets
- Validate model performance before integration
- Keep static data as fallback

### Risk: ADB Connection Complexity
**Mitigation**:
- Document wallet setup clearly
- Provide connection test scripts
- Use environment variables for configuration

### Risk: Model Performance
**Mitigation**:
- Set minimum AUC threshold (0.70)
- Test with multiple datasets
- Consider AutoML if XGBoost fails

### Risk: API Performance
**Mitigation**:
- Implement response caching
- Optimize database queries
- Use connection pooling

### Trade-off: Simplicity vs. Features
**Decision**: Prioritize simplicity for demo
- Single model version (no A/B testing)
- Batch scoring (not real-time per customer)
- Basic error handling (sufficient for demo)

## Migration Plan

1. **Phase 1**: Build backend API with mock data
2. **Phase 2**: Integrate ML pipeline and real model
3. **Phase 3**: Connect frontend to API
4. **Phase 4**: Remove static data dependency (optional)

**Rollback**: Frontend falls back to static data if API fails

## Open Questions

1. Which specific Kaggle dataset to use? (Need to research)
2. Should we support model retraining on schedule? (Not in scope, but consider)
3. API authentication for production? (Not needed for demo)
4. Caching strategy for API responses? (Implement basic caching)
