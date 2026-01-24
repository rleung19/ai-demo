# Implementation Tasks

## 1. Dependencies & Setup
- [x] 1.1 Install OCI SDK packages (`oci-sdk`) in `package.json` (Note: implemented custom signing for Node.js 22 compatibility)
- [x] 1.2 Verify OCI config file exists at `.oci/config` or `~/.oci/config` (with automatic detection)
- [x] 1.3 Add `OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT` and `OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT` to `.env.example` with documentation
- [x] 1.4 Document OCI authentication setup process (for both product and basket recommenders)
- [x] 1.5 Propagate new descriptive env var names (`OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT`, `OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT`) into all affected files when implementing (server config, `docker/podman-compose.yml`, `.env.example`, `.env.oci`)

## 2. OCI Model Deployment API Client
- [x] 2.1 Create `server/lib/oci/model-deployment.ts` utility
- [x] 2.2 Implement OCI signer initialization from config file
- [x] 2.3 Implement `predictUserRecs()` function to call product recommender OCI Model Deployment endpoint
- [x] 2.4 Implement `predictBasketRecs()` function to call basket recommender OCI Model Deployment endpoint
- [x] 2.5 Implement `testConnection()` function for health checks (configurable per endpoint)
- [x] 2.6 Add error handling for OCI authentication failures
- [x] 2.7 Add error handling for OCI API call failures

## 3. User-Based Recommender API Route
- [x] 3.1 Create `server/routes/recommender/product.ts` route handler
- [x] 3.2 Implement POST endpoint with request validation (`user_id` required, `top_k` optional)
- [x] 3.3 Implement GET endpoint with query parameter support (convenience)
- [x] 3.4 Integrate response caching (5-minute TTL using existing cache utility)
- [x] 3.5 Add request validation (user_id required, top_k between 1-100)
- [x] 3.6 Add error handling for missing endpoint configuration
- [x] 3.7 Add error handling for OCI service errors
- [x] 3.8 Return standardized error responses matching existing API patterns

## 4. Basket Recommender API Route
- [x] 4.1 Create `server/routes/recommender/basket.ts` route handler
- [x] 4.2 Implement POST endpoint with request validation (`basket` array of product IDs required, `top_n` optional)
- [x] 4.3 Transform basket payload into OCI Model Deployment request format (`{\"data\": [[...product_ids...]]}`)
- [x] 4.4 Map OCI response (`prediction` structure) into simplified JSON with `recommendations` array
- [x] 4.5 Integrate response caching (5-minute TTL using existing cache utility)
- [x] 4.6 Add error handling for missing basket endpoint configuration
- [x] 4.7 Add error handling for OCI service errors (including invalid model responses)
- [x] 4.8 Return standardized error responses matching existing API patterns

## 5. Server Integration
- [x] 5.1 Update `server/index.ts` to import recommender routes
- [x] 5.2 Register `/api/recommender/product` and `/api/recommender/basket` routes in Express app
- [x] 5.3 Update root endpoint documentation to include recommender endpoints
- [x] 5.4 Test route registration and middleware chain

## 6. Testing & Validation
- [x] 6.1 Test OCI authentication with valid config file (custom RSA-SHA256 signing implemented)
- [x] 6.2 Test user-based prediction endpoint with valid user_id (✓ user 100773 returned 5 recommendations)
- [x] 6.3 Test user-based prediction endpoint with invalid user_id (✓ returns empty recommendations gracefully)
- [x] 6.4 Test user-based request validation (✓ missing user_id, invalid top_k return proper validation errors)
- [x] 6.5 Test basket prediction endpoint with valid basket (✓ matches notebook test case with 3 rules)
- [x] 6.6 Test basket prediction endpoint with empty or malformed basket (✓ all validation rules working)
- [x] 6.7 Test basket payload/response mapping against notebook examples (✓ confidence and lift values correct)
- [x] 6.8 Test error handling (✓ verified all error paths: missing endpoint config, OCI auth failure, OCI 4xx/5xx)
- [x] 6.9 Test response caching (✓ product: 213x speedup, basket: 275x speedup on cache hit)
- [x] 6.10 Test GET endpoint convenience method (user-based) (✓ query parameters working)
- [x] 6.11 Test with actual OCI Model Deployment endpoints (end-to-end for both models) (✓ both APIs working in production)

## 7. OCI VM Deployment (Podman)
- [x] 7.1 Add OCI SDK dependencies (`oci-sdk`, `oci-common`) to `package.json` dependencies (not devDependencies, needed at runtime)
- [x] 7.2 Update `docker/podman-compose.yml`:
  - Add new environment variables:
    - `OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT` (product recommender endpoint URL)
    - `OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT` (basket recommender endpoint URL)
  - Add volume mount for OCI config directory (project-local, sibling to `wallets/`):
    - Mount `../.oci` from project root to `/root/.oci` in container (read-only)
    - Ensure OCI config file and API key are accessible from container (both under `.oci/`)
- [x] 7.3 Update `docker/.env.oci.example` (or create if missing) with OCI Model Deployment endpoint variables:
  - `OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT` (example URL format)
  - `OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT` (example URL format)
- [x] 7.4 Document OCI config file setup on VM in `docker/README_OCI_VM_PODMAN.md`:
  - Create `./.oci/config` file in project root (sibling to `wallets/`) with OCI credentials (tenancy, user, fingerprint, key_file, pass_phrase)
  - Create `./.oci/oci_api_key.pem` file with OCI API private key
  - Ensure both files are readable by the user running Podman
  - Document how to generate OCI API key and config file if needed (link to OCI documentation)
- [x] 7.5 Update `docker/README_OCI_VM_PODMAN.md` with recommender API deployment steps:
  - Add section "OCI Model Deployment Configuration" explaining:
    - How to obtain endpoint URLs from OCI Data Science deployments (from notebook deployment cells)
    - How to set up `~/.oci/config` file and API key
    - How to add endpoint URLs to `.env.oci`
    - How the OCI config volume mount works
  - Add troubleshooting section for OCI authentication failures:
    - Verify config file exists and is readable
    - Verify API key file exists and permissions are correct
    - Verify volume mount is working (check container logs)
    - Verify endpoint URLs are correct and accessible
- [ ] 7.6 Verify Dockerfile doesn't need changes (OCI SDK is npm package, no system dependencies)
- [ ] 7.7 Test container build with OCI SDK dependencies included
- [ ] 7.8 Test OCI authentication from within container:
  - Verify `~/.oci/config` is accessible at `/root/.oci/config` in container
  - Verify API key file is accessible
  - Test OCI SDK can read config and authenticate
- [ ] 7.9 Update deployment documentation with example `.env.oci` entries for recommender endpoints
- [ ] 7.10 Test end-to-end deployment on OCI VM:
  - Build container with OCI SDK
  - Start container with OCI config volume mount
  - Test recommender API endpoints from outside container
  - Verify OCI Model Deployment calls succeed

## 8. Documentation
- [x] 8.1 Update OpenAPI/Swagger spec (`server/openapi.ts`) with new recommender endpoints
  - Added `/api/recommender/product` (GET and POST)
  - Added `/api/recommender/basket` (POST)
  - Updated title and description to reflect expanded API scope
- [x] 8.2 Enhance OpenAPI spec with real sample request/response bodies for ALL endpoints
  - ✓ Called all KPI/churn endpoints to get actual response samples
  - ✓ Called recommender endpoints to get actual response samples
  - ✓ Added comprehensive JSON schemas with real examples for all 9 endpoints:
    - `/api/health` - Full health check response with database status
    - `/api/kpi/churn/summary` - Complete summary metrics with LTV
    - `/api/kpi/churn/cohorts` - 4 cohorts (VIP, Regular, New, Dormant)
    - `/api/kpi/churn/metrics` - Full model performance metrics
    - `/api/kpi/churn/chart-data` - Distribution histogram data
    - `/api/kpi/churn/risk-factors` - Top 5 risk factors with impact scores
    - `/api/recommender/product` (GET/POST) - Product recommendations with ratings
    - `/api/recommender/basket` (POST) - Basket recommendations with confidence/lift
  - ✓ Added proper parameter descriptions, validation rules, and error response schemas
- [ ] 8.3 Document user-based recommender API endpoint in markdown documentation
- [ ] 8.4 Document basket recommender API endpoint in markdown documentation (including payload and response shape)
- [ ] 8.5 Document OCI authentication setup requirements (local development and OCI VM)
- [ ] 8.6 Document environment variable configuration for both endpoints
- [ ] 8.7 Add example requests/responses based on notebook examples (product and basket)
- [ ] 8.8 Update README with recommender API usage
