# recommender-api Specification

## Purpose
TBD - created by archiving change add-recommender-api-wrapper. Update Purpose after archive.
## Requirements
### Requirement: User-Based Recommender Prediction Endpoint
The system SHALL provide a REST API endpoint `POST /api/recommender/product` that returns product recommendations for a given user.

The endpoint SHALL:
- Accept JSON request body with `user_id` (required) and `top_k` (optional, default 10)
- Call the product recommender OCI Model Deployment endpoint with OCI authentication
- Return product recommendations with predicted ratings
- Cache responses for 5 minutes to reduce OCI API calls
- Validate request parameters (user_id required, top_k between 1-100)

#### Scenario: Get recommendations for user
- **WHEN** client sends `POST /api/recommender/product` with `{"user_id": "100773", "top_k": 5}`
- **THEN** API validates request parameters
- **AND** API calls the product recommender OCI Model Deployment endpoint with OCI authentication
- **AND** API returns JSON response with user_id, recommendations array, and message
- **AND** response includes HTTP 200 status code
- **AND** recommendations array contains product_id and rating for each recommendation

#### Scenario: Handle user with no recommendations
- **WHEN** client requests recommendations for user_id not in model
- **THEN** API calls the product recommender OCI Model Deployment endpoint
- **AND** API returns JSON response with empty recommendations array
- **AND** response message indicates "No recommendations found"
- **AND** response includes HTTP 200 status code

#### Scenario: Request validation failure (user-based)
- **WHEN** client sends request without `user_id` field
- **THEN** API returns HTTP 400 with validation error message
- **AND** response indicates `user_id` is required

#### Scenario: Invalid top_k parameter
- **WHEN** client sends request with `top_k` outside valid range (1-100)
- **THEN** API returns HTTP 400 with validation error message
- **AND** response indicates `top_k` must be between 1 and 100

#### Scenario: Missing product recommender OCI endpoint configuration
- **WHEN** `OCI_MODEL_DEPLOYMENT_ENDPOINT` environment variable is not set
- **THEN** API returns HTTP 503 with configuration error message
- **AND** response indicates endpoint not configured

#### Scenario: Response caching (user-based)
- **WHEN** client requests recommendations for same user_id and top_k within 5 minutes
- **THEN** API returns cached response without calling OCI endpoint
- **AND** response includes HTTP 200 status code

### Requirement: User-Based Recommender GET Endpoint
The system SHALL provide a REST API endpoint `GET /api/recommender/product` as a convenience method for simple user-based use cases.

The endpoint SHALL:
- Accept query parameters `user_id` (required) and `top_k` (optional)
- Convert GET request to POST format internally
- Return same response format as POST endpoint

#### Scenario: Get recommendations via GET
- **WHEN** client sends `GET /api/recommender/product?user_id=100773&top_k=5`
- **THEN** API converts query parameters to POST request format
- **AND** API processes request using same logic as POST endpoint
- **AND** API returns same JSON response format as POST endpoint

### Requirement: Basket Recommender Prediction Endpoint
The system SHALL provide a REST API endpoint `POST /api/recommender/basket` that returns complementary product recommendations for a given basket of products.

The endpoint SHALL:
- Accept JSON request body with `basket` (required, array of product IDs) and `top_n` (optional, default 3)
- Transform the basket into the OCI Model Deployment payload format (`{"data": [[...product_ids...]]}`)
- Call the basket recommender OCI Model Deployment endpoint with OCI authentication
- Map the OCI response `prediction` structure into a simplified JSON response with `recommendations` array
- Cache responses for 5 minutes to reduce OCI API calls
- Validate request parameters (basket required, non-empty array of strings; top_n > 0)

#### Scenario: Get basket recommendations
- **WHEN** client sends `POST /api/recommender/basket` with `{"basket": ["B01CG1J7XG", "B0BKZHSDGP", "B094H5S3TY"], "top_n": 3}`
- **THEN** API validates request parameters
- **AND** API builds OCI payload `{"data": [["B01CG1J7XG", "B0BKZHSDGP", "B094H5S3TY"]]}`
- **AND** API calls the basket recommender OCI Model Deployment endpoint with OCI authentication
- **AND** API maps the OCI `prediction` response into `recommendations` array with `products`, `confidence`, and `lift`
- **AND** response includes HTTP 200 status code

#### Scenario: Empty or invalid basket
- **WHEN** client sends request with missing `basket` field or an empty array
- **THEN** API returns HTTP 400 with validation error message
- **AND** response indicates `basket` must be a non-empty array of product IDs

#### Scenario: Missing basket recommender OCI endpoint configuration
- **WHEN** `OCI_BASKET_MODEL_DEPLOYMENT_ENDPOINT` environment variable is not set
- **THEN** API returns HTTP 503 with configuration error message
- **AND** response indicates basket endpoint not configured

#### Scenario: Response caching (basket-based)
- **WHEN** client requests recommendations for the same basket and top_n within 5 minutes
- **THEN** API returns cached response without calling OCI endpoint
- **AND** response includes HTTP 200 status code

### Requirement: OCI Authentication
The system SHALL authenticate with OCI Model Deployment using server-side OCI SDK.

The authentication SHALL:
- Use OCI config file at `~/.oci/config` for credentials
- Initialize OCI signer on first request (lazy initialization)
- Handle authentication errors gracefully
- Not expose OCI credentials to clients

#### Scenario: OCI authentication success
- **WHEN** OCI config file exists with valid credentials
- **THEN** API initializes OCI signer successfully
- **AND** API signs HTTP requests to product and basket OCI Model Deployment endpoints
- **AND** OCI accepts authenticated requests

#### Scenario: OCI authentication failure
- **WHEN** OCI config file is missing or contains invalid credentials
- **THEN** API returns HTTP 503 error
- **AND** error message indicates OCI authentication failure
- **AND** error does not expose credential details

### Requirement: Error Handling
The system SHALL handle errors from OCI Model Deployment and return standardized error responses.

Error responses SHALL:
- Use consistent error format matching existing API patterns
- Include error type, message, and fallback flag
- Return appropriate HTTP status codes (400 for validation, 503 for service errors)
- Log errors for debugging without exposing sensitive information

#### Scenario: OCI service unavailable
- **WHEN** any OCI Model Deployment endpoint is unreachable or returns error
- **THEN** API returns HTTP 503 with OCI service error message
- **AND** response includes fallback flag set to true
- **AND** error is logged for debugging

---

