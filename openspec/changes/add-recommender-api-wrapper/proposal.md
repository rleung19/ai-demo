# Change: Add Recommender API Wrapper

## Why
The recommender model is trained and deployed on OCI Data Science Notebook sessions using Oracle ADS, and deployed to OCI Model Deployment. Clients calling the OCI Model Deployment endpoint directly require OCI authentication credentials (API keys, config files), which is not practical for frontend applications or external clients. We need a wrapper API in our existing Express server that handles OCI authentication internally and provides a simple REST API for recommender predictions.

## What Changes
- **New API Endpoint (User-Based Recommender)**: `POST /api/recommender/product` - Wrapper for OCI Model Deployment *product* recommender predictions
- **New API Endpoint (Basket Recommender)**: `POST /api/recommender/basket` - Wrapper for OCI Data Science *basket association* model; recommends complementary products for a given basket
- **OCI Authentication Utility**: Server-side OCI SDK integration to authenticate and call OCI Model Deployment endpoints
- **Response Caching**: 5-minute cache for recommender predictions (user-based and basket-based) to reduce OCI API calls
- **Error Handling**: Standardized error responses for OCI service failures
- **Environment Configuration**: Support for `OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT` (user-based) and `OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT` (basket-based) environment variables
- **GET Endpoint Support**: Convenience GET endpoint with query parameters for simple use cases (user-based recommender) at `GET /api/recommender/product`

## Impact
- **New Capability**: `recommender-api` - Wrapper API for OCI Model Deployment recommender models (user-based and basket-based)
- **Modified Capability**: None (new capability, doesn't modify existing APIs)
- **New Code**:
  - `server/lib/oci/model-deployment.ts` - OCI authentication and API client utility (shared by both recommenders)
  - `server/routes/recommender/product.ts` - User-based recommender prediction endpoint
  - `server/routes/recommender/basket.ts` - Basket recommender prediction endpoint
  - Updates to `server/index.ts` - Register new routes
- **New Dependencies**: `oci-sdk`, `oci-common` packages
- **New Environment Variables**:
  - `OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT` (required for product recommender deployment endpoint URL)
  - `OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT` (required for basket recommender deployment endpoint URL)
- **Infrastructure**: 
  - Requires OCI config file (`~/.oci/config`) on server for authentication
  - OCI VM deployment updates: Add OCI SDK dependencies, configure OCI credentials, add environment variables to `podman-compose.yml` and `.env.oci`

## Example Requests & Responses

### Product Recommender (User-Based)

**Request**

```http
POST /api/recommender/product HTTP/1.1
Content-Type: application/json

{
  "user_id": "100773",
  "top_k": 5
}
```

**Response (modeled after `Recommender-2.ipynb` final cell)**

```json
{
  "user_id": "100773",
  "recommendations": [
    { "product_id": "B099DDH2RG", "rating": 3.845543881667073 },
    { "product_id": "B07SN9RS13", "rating": 3.8321897411770967 },
    { "product_id": "B08SC3KCGM", "rating": 3.798262404007028 },
    { "product_id": "B09BF5VNBS", "rating": 3.7935598359514113 },
    { "product_id": "B000K3D982", "rating": 3.783557811959144 }
  ],
  "message": "Success"
}
```

### Basket Recommender

**Request**

```http
POST /api/recommender/basket HTTP/1.1
Content-Type: application/json

{
  "basket": ["B01CG1J7XG", "B0BKZHSDGP", "B094H5S3TY"],
  "top_n": 3
}
```

**Response (modeled after `Basket-2.ipynb` final cell, normalized by wrapper)**

```json
{
  "basket": ["B01CG1J7XG", "B0BKZHSDGP", "B094H5S3TY"],
  "recommendations": [
    {
      "products": ["B01CG1J7XG", "B07KX2N7TM", "B0BFPXJ2YD"],
      "confidence": 1.0,
      "lift": 19.0
    },
    {
      "products": ["B07KX2N7TM", "B094H5S3TY"],
      "confidence": 1.0,
      "lift": 19.0
    },
    {
      "products": ["B0BFPXJ2YD", "B0BKZHSDGP"],
      "confidence": 1.0,
      "lift": 19.0
    }
  ],
  "message": "Success"
}
```

## OCI VM Deployment Changes

The recommender API wrapper requires additional configuration for OCI VM deployment using Podman:

### Modified Files

1. **`package.json`**
   - Add `oci-sdk` and `oci-common` to `dependencies` (runtime dependencies, not devDependencies)

2. **`docker/podman-compose.yml`**
   - Add environment variables:
     ```yaml
     OCI_MODEL_DEPLOYMENT_ENDPOINT: "${OCI_MODEL_DEPLOYMENT_ENDPOINT}"
     OCI_BASKET_MODEL_DEPLOYMENT_ENDPOINT: "${OCI_BASKET_MODEL_DEPLOYMENT_ENDPOINT}"
     ```

3. **`docker/.env.oci`** (on VM, not committed)
   - Add OCI Model Deployment endpoint URLs:
     ```bash
     OCI_MODEL_DEPLOYMENT_ENDPOINT=https://modeldeployment.ap-singapore-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.ap-singapore-1.amaaaaaahxv2vbyapmduolpu3xvaq6q2v2s7le6duh2jeg3xlnxyjxvebxra
     OCI_BASKET_MODEL_DEPLOYMENT_ENDPOINT=https://modeldeployment.ap-singapore-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.ap-singapore-1.amaaaaaahxv2vbya7xn4ginlgqci3bzxo5udywfqzhcuti7pypk4j4my4ita
     ```

### New VM Setup Steps

4. **OCI Config File Setup** (one-time on VM)
   - Create `~/.oci/config` file with OCI credentials:
     ```ini
     [DEFAULT]
     tenancy=ocid1.tenancy.oc1..aaaaaaa...
     user=ocid1.user.oc1..aaaaaaa...
     fingerprint=aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99
     key_file=~/.oci/oci_api_key.pem
     pass_phrase=your_passphrase_if_any
     region=ap-singapore-1
     ```
   - Ensure the config file and API key file are readable by the user running Podman
   - The OCI SDK in the container will read this config file to authenticate with OCI Model Deployment

5. **`docker/README_OCI_VM_PODMAN.md`**
   - Add section "OCI Model Deployment Configuration" explaining:
     - How to obtain endpoint URLs from OCI Data Science deployments
     - How to set up `~/.oci/config` file
     - How to add endpoint URLs to `.env.oci`
     - Troubleshooting OCI authentication errors

### Modified Deployment Configuration

6. **`docker/podman-compose.yml`** - Volume mount addition
   - Add volume mount for OCI config directory:
     ```yaml
     volumes:
       - ~/.oci:/root/.oci:ro  # Mount OCI config directory (read-only)
     ```
   - This allows the container to access `~/.oci/config` and `~/.oci/oci_api_key.pem` from the VM host

### No Changes Required

- **`docker/Dockerfile`**: No changes needed - OCI SDK is npm packages, no system dependencies
- **Port mappings**: No new ports needed - recommender APIs use existing Express server (port 3001)
