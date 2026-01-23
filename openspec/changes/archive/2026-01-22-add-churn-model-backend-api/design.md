# Design: Churn Model Backend API

## Context
The AI workshop demo needs a production-ready churn prediction system. Currently, KPI #1 displays static synthetic data. We need to connect to Oracle ADB Serverless, train real ML models, and serve predictions via REST API. The existing demo data in ADMIN schema produces low-quality models (AUC ~0.50), so we need better datasets.

**Stakeholders**: Workshop participants, demo audience
**Constraints**: 
- Must work with Oracle ADB Serverless
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
- Supports both Python (local model training) and Node.js (API server)
- Well-documented in Oracle documentation

**Alternatives Considered**:
- Connection string with credentials: Less secure, not recommended for ADB

### Decision: Model Algorithm
**Chosen**: XGBoost via local training (pickle files)
**Rationale**:
- XGBoost is proven for churn prediction
- Local training provides better performance (AUC 0.9269 vs 0.50 with OML4Py)
- More control over training process and hyperparameters
- Easier automation and deployment
- Pickle files can be versioned and stored in repository

**Alternatives Considered**:
- OML4Py (in-database): Rejected due to poor performance (AUC ~0.50)
- Neural Networks: Overkill for this use case, slower training
- Logistic Regression: Simpler but typically lower performance
- AutoML: Considered but XGBoost performs well enough

### Decision: Model Deployment
**Chosen**: Local pickle files + Direct SQL scoring in API
**Rationale**:
- Models saved as pickle files in `models/` directory
- API loads model from pickle file (finds latest automatically)
- Scores users by loading features from database and applying model
- Stores predictions back to `OML.CHURN_PREDICTIONS` table
- No need for separate model serving infrastructure
- Sufficient for demo scale

**Alternatives Considered**:
- OML Datastore: Rejected due to poor model performance
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
         │ SQL (load features)
         │
┌────────▼─────────────────┐
│  Oracle ADB Serverless  │
│  - OML Schema           │
│    - Dataset tables     │
│    - Feature views      │
│    - CHURN_PREDICTIONS  │
│  - ADMIN Schema         │
│    - (existing demo)    │
└─────────────────────────┘

┌─────────────────────────┐
│  ML Pipeline (Python)   │
│  - Data ingestion       │
│  - Feature engineering  │
│  - Local model training │
│  - Model evaluation     │
│  - Save pickle files    │
└─────────────────────────┘
         │
         │ Load model
         │
┌────────▼─────────────────┐
│  Model Files (pickle)   │
│  - models/*.pkl          │
│  - models/*.json         │
└─────────────────────────┘
```

## Data Flow

1. **Training Pipeline**:
   - Load dataset → OML schema tables
   - Create feature views (`OML.CHURN_USER_FEATURES`)
   - Train XGBoost model locally (Python script)
   - Evaluate model (AUC 0.9269 achieved)
   - Save model as pickle file + metadata JSON to `models/` directory

2. **API Request Flow**:
   - Frontend requests `/api/kpi/churn/summary`
   - API loads latest model from `models/` directory (pickle file)
   - API loads user features from `OML.CHURN_USER_FEATURES` view
   - API scores users with loaded model
   - API stores predictions in `OML.CHURN_PREDICTIONS` table
   - API aggregates results (cohorts, metrics) from predictions table
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
- Local training approach achieves AUC 0.9269 (exceeds threshold)

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

## OCI Deployment

### Decision: Deployment Platform
**Chosen**: OCI VM (Ubuntu ARM64) with Podman containers
**Rationale**:
- Containerized deployment for consistency and portability
- Podman is available on OCI VMs (rootless, no daemon)
- Build directly on VM for simplicity
- Easy integration with existing Caddy reverse proxy
- Supports Oracle Instant Client and wallet mounting
- ARM64 architecture provides cost-effective compute options

**Alternatives Considered**:
- OCI Container Instances: More expensive, less control
- OCI Kubernetes (OKE): Overkill for demo, more complex
- Direct VM deployment: Less portable, harder to manage
- x86-based VMs: More expensive, ARM64 sufficient for demo workload

### Deployment Architecture

```
┌─────────────────────────────────────────────┐
│  OCI VM (Ubuntu ARM64)                     │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Caddy (Host Service)                 │  │
│  │  - TLS termination                    │  │
│  │  - https://ecomm.40b5c371.nip.io     │  │
│  │  - reverse_proxy → localhost:3002    │  │
│  └───────────────┬────────────────────────┘  │
│                  │                           │
│  ┌───────────────▼────────────────────────┐  │
│  │  Podman Container (ecomm)             │  │
│  │  ┌─────────────────────────────────┐ │  │
│  │  │ npm run dev:all                  │ │  │
│  │  │  ├─ Next.js (container:3000)    │ │  │
│  │  │  │   └─ mapped to host:3002     │ │  │
│  │  │  └─ Express API (container:3001) │ │  │
│  │  │      └─ mapped to host:3003     │ │  │
│  │  └─────────────────────────────────┘ │  │
│  │                                        │  │
│  │  Oracle Instant Client (baked in)     │  │
│  │  - /opt/oracle/instantclient_23_26   │  │
│  │    (copied from opt/oracle at        │  │
│  │     project root during build)        │  │
│  │                                        │  │
│  │  Volume Mount (read-only):            │  │
│  │  - ../wallets/Wallet_HHZJ2H81DDJWN1DM │  │
│  │    → /opt/oracle/wallet               │  │
│  │    (from ~/compose/demo/              │  │
│  │     oracle-demo-ecomm/wallets/)       │  │
│  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                  │
                  │ TLS/HTTPS (via Caddy)
                  │
┌─────────────────▼─────────────────┐
│  Oracle ADB Serverless              │
│  (External, wallet-based auth)      │
└─────────────────────────────────────┘
```

### Deployment Components

1. **Container Image** (`ecomm:latest`):
   - Multi-stage Dockerfile build (ARM64 compatible)
   - Oracle Instant Client (23.26) baked into image at `/opt/oracle/instantclient_23_26`
   - Instant Client copied from `opt/oracle` directory at project root during build
   - On VM: Instant Client located at `~/compose/demo/oracle-demo-ecomm/opt/oracle/instantclient_23_26/`
   - Production build of Next.js app
   - Express API server
   - Runs `npm run dev:all` (starts both Next.js on port 3000 and Express on port 3001)
   - Development mode suitable for demo environment

2. **Podman Compose Configuration**:
   - Service: `app` (container name: `ecomm`)
   - Port mappings: Host 3002 → Container 3000 (Next.js), Host 3003 → Container 3001 (Express API)
   - Environment variables from `.env.oci`
   - **Single volume mount** (read-only): `../wallets/Wallet_HHZJ2H81DDJWN1DM` → `/opt/oracle/wallet`
   - Wallet location on VM: `~/compose/demo/oracle-demo-ecomm/wallets/Wallet_HHZJ2H81DDJWN1DM`
   - Oracle Instant Client baked into image (copied from project root `opt/oracle` during build, not volume mounted)

3. **Caddy Integration**:
   - Runs as host service (not containerized)
   - Reverse proxy with TLS termination
   - Domain: `ecomm.40b5c371.nip.io` (nip.io for dynamic DNS)
   - Routes HTTPS traffic to container on `localhost:3002` (Next.js)
   - Frontend configured with `NEXT_PUBLIC_API_URL=https://ecomm.40b5c371.nip.io`

### Deployment Process

1. **VM Setup**:
   - OCI VM: Ubuntu ARM64 instance
   - Install Podman and podman-compose
   - Clone repository to `~/compose/demo/oracle-demo-ecomm`
   - Download and extract Oracle Instant Client (ARM64 version) to `opt/oracle/instantclient_23_26/` at project root
   - Final structure: `~/compose/demo/oracle-demo-ecomm/opt/oracle/instantclient_23_26/`
   - Upload ADB wallet to `~/compose/demo/oracle-demo-ecomm/wallets/Wallet_HHZJ2H81DDJWN1DM`

2. **Build and Run**:
   - Build image: `podman-compose build app`
   - Start container: `podman-compose up -d app`
   - Configure Caddy reverse proxy

3. **Updates**:
   - Pull latest code: `git pull`
   - Rebuild and restart: `podman-compose build app && podman-compose up -d app`

### Deployment Considerations

- **VM Architecture**: Ubuntu ARM64 (cost-effective, sufficient for demo workload)
- **Oracle Instant Client**: 
  - Located at project root: `~/compose/demo/oracle-demo-ecomm/opt/oracle/instantclient_23_26/`
  - Copied into Docker image during build (not volume mounted)
  - Dockerfile copies from `../opt/oracle` (relative to `docker/` directory)
- **ADB Wallet**: 
  - Only volume mount in podman-compose.yml
  - Mounted as read-only volume: `../wallets/Wallet_HHZJ2H81DDJWN1DM` → `/opt/oracle/wallet`
  - Location on VM: `~/compose/demo/oracle-demo-ecomm/wallets/Wallet_HHZJ2H81DDJWN1DM`
- **Environment Variables**: Stored in `.env.oci` (not committed to Git)
- **Port Configuration**: 
  - Host port 3002 → Container port 3000 (Next.js)
  - Host port 3003 → Container port 3001 (Express API)
  - Ports chosen to avoid conflicts with other services
- **Caddy Integration**: Runs on host (not containerized), proxies HTTPS to container
- **Development Mode**: Container runs `npm run dev:all` which starts both services (suitable for demo, not production)
- **API URL Configuration**: Frontend uses `NEXT_PUBLIC_API_URL=https://ecomm.40b5c371.nip.io` (Caddy domain)

## Open Questions

1. Which specific Kaggle dataset to use? (Need to research)
2. Should we support model retraining on schedule? (Not in scope, but consider)
3. API authentication for production? (Not needed for demo)
4. Caching strategy for API responses? (Implement basic caching)
5. Production deployment strategy? (OCI VM with Podman - decided)
