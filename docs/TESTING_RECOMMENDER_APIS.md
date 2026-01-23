# Testing Recommender APIs Locally

This guide shows how to test the Product Recommender and Basket Recommender APIs locally.

## Prerequisites

### 1. OCI Configuration Setup

The recommender APIs require OCI authentication to call the deployed model endpoints. Set up your OCI config:

```bash
# Create OCI config directory (if it doesn't exist)
mkdir -p ~/.oci

# Create OCI config file
cat > ~/.oci/config << 'EOF'
[DEFAULT]
user=ocid1.user.oc1..aaaaaaa...
fingerprint=aa:bb:cc:dd:ee:ff:11:22:33:44:55:66:77:88:99:aa
tenancy=ocid1.tenancy.oc1..aaaaaaa...
region=us-chicago-1
key_file=~/.oci/oci_api_key.pem
pass_phrase=your_api_key_passphrase_if_any
EOF

# Copy your OCI API private key
# (Generate this in OCI Console: Identity > Users > API Keys)
cp /path/to/your/oci_api_key.pem ~/.oci/oci_api_key.pem

# Set secure permissions
chmod 600 ~/.oci/config
chmod 600 ~/.oci/oci_api_key.pem
```

**Note**: If you don't have an OCI API key yet:
1. Go to OCI Console → Identity → Users → Your User → API Keys
2. Click "Add API Key"
3. Download the private key and copy the fingerprint
4. Add the fingerprint and key file path to `~/.oci/config`

### 2. Environment Variables

Add the OCI Model Deployment endpoint URLs to your `.env` file:

```bash
# Add to .env file
OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT=https://modeldeployment.us-chicago-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.us-chicago-1.abc123xyz
OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT=https://modeldeployment.us-chicago-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.us-chicago-1.def456uvw
```

**Important**: 
- Get these URLs from your OCI Data Science Notebook deployment cells (from `Recommender-2.ipynb` and `Basket-2.ipynb`)
- Use the **base URL** without the `/predict` suffix (it will be added automatically)
- The URLs should look like: `https://modeldeployment.{region}.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.{region}.{id}`

## Starting the Server

### Option 1: Start API Server Only (Recommended for Testing)

```bash
npm run server:dev
```

The server will start on `http://localhost:3001` (or the port specified in `API_PORT`).

### Option 2: Start Both Frontend and API Server

```bash
npm run dev:all
```

This starts:
- Next.js frontend on `http://localhost:3000`
- API server on `http://localhost:3001`

## Testing the APIs

### 1. Product Recommender API

#### Endpoint
- **POST** `/api/recommender/product`
- **GET** `/api/recommender/product?user_id={user_id}&top_k={top_k}` (convenience method)

#### Sample Request (POST)

```bash
curl -X POST http://localhost:3001/api/recommender/product \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "100773",
    "top_k": 5
  }'
```

#### Sample Request (GET - Convenience)

```bash
curl "http://localhost:3001/api/recommender/product?user_id=100773&top_k=5"
```

#### Expected Response

```json
{
  "user_id": "100773",
  "recommendations": [
    {
      "product_id": "B099DDH2RG",
      "rating": 3.845543881667073
    },
    {
      "product_id": "B07SN9RS13",
      "rating": 3.8321897411770967
    },
    {
      "product_id": "B08SC3KCGM",
      "rating": 3.798262404007028
    },
    {
      "product_id": "B09BF5VNBS",
      "rating": 3.7935598359514113
    },
    {
      "product_id": "B000K3D982",
      "rating": 3.783557811959144
    }
  ],
  "message": "Success"
}
```

#### Request Parameters

- **`user_id`** (required): String - User identifier
- **`top_k`** (optional): Integer between 1-100, default: 10 - Number of recommendations to return

#### Error Responses

**Missing user_id:**
```json
{
  "error": "Validation failed",
  "message": "Invalid request parameters",
  "details": {
    "errors": ["user_id is required"]
  }
}
```

**Invalid top_k:**
```json
{
  "error": "Validation failed",
  "message": "Invalid request parameters",
  "details": {
    "errors": ["top_k must be a number between 1 and 100"]
  }
}
```

**Missing endpoint configuration:**
```json
{
  "error": "Internal server error",
  "message": "OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT is not configured in environment variables",
  "fallback": true
}
```

**OCI authentication error:**
```json
{
  "error": "OCI service error",
  "message": "OCI model deployment error: 401 Unauthorized - ...",
  "fallback": true
}
```

---

### 2. Basket Recommender API

#### Endpoint
- **POST** `/api/recommender/basket`

#### Sample Request

```bash
curl -X POST http://localhost:3001/api/recommender/basket \
  -H "Content-Type: application/json" \
  -d '{
    "basket": ["B01CG1J7XG", "B0BKZHSDGP", "B094H5S3TY"],
    "top_n": 3
  }'
```

#### Expected Response

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

#### Request Parameters

- **`basket`** (required): Array of strings - Product IDs currently in the basket
- **`top_n`** (optional): Integer between 1-100, default: 3 - Number of association rules/recommendations to return

#### Error Responses

**Missing or empty basket:**
```json
{
  "error": "Validation failed",
  "message": "Invalid request parameters",
  "details": {
    "errors": ["basket must be a non-empty array of product IDs"]
  }
}
```

**Invalid basket items:**
```json
{
  "error": "Validation failed",
  "message": "Invalid request parameters",
  "details": {
    "errors": ["basket must contain only non-empty string product IDs"]
  }
}
```

**Missing endpoint configuration:**
```json
{
  "error": "Internal server error",
  "message": "OCI_BASKET_RECOMMENDER_MODEL_ENDPOINT is not configured in environment variables",
  "fallback": true
}
```

**OCI authentication error:**
```json
{
  "error": "OCI service error",
  "message": "OCI model deployment error: 401 Unauthorized - ...",
  "fallback": true
}
```

---

## Testing with HTTPie (Alternative to curl)

If you have `httpie` installed, you can use a more readable syntax:

### Product Recommender

```bash
# POST request
http POST http://localhost:3001/api/recommender/product \
  user_id=100773 \
  top_k=5

# GET request
http GET http://localhost:3001/api/recommender/product \
  user_id==100773 \
  top_k==5
```

### Basket Recommender

```bash
http POST http://localhost:3001/api/recommender/basket \
  basket:='["B01CG1J7XG", "B0BKZHSDGP", "B094H5S3TY"]' \
  top_n=3
```

---

## Testing with JavaScript/Node.js

```javascript
// Product Recommender
const response = await fetch('http://localhost:3001/api/recommender/product', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: '100773',
    top_k: 5
  })
});
const data = await response.json();
console.log(data);

// Basket Recommender
const basketResponse = await fetch('http://localhost:3001/api/recommender/basket', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    basket: ['B01CG1J7XG', 'B0BKZHSDGP', 'B094H5S3TY'],
    top_n: 3
  })
});
const basketData = await basketResponse.json();
console.log(basketData);
```

---

## Testing with Python

```python
import requests

# Product Recommender
response = requests.post(
    'http://localhost:3001/api/recommender/product',
    json={
        'user_id': '100773',
        'top_k': 5
    }
)
print(response.json())

# Basket Recommender
basket_response = requests.post(
    'http://localhost:3001/api/recommender/basket',
    json={
        'basket': ['B01CG1J7XG', 'B0BKZHSDGP', 'B094H5S3TY'],
        'top_n': 3
    }
)
print(basket_response.json())
```

---

## Response Caching

Both APIs implement **5-minute response caching**. If you make the same request twice within 5 minutes, the second request will return the cached response (much faster).

To test caching:
1. Make a request and note the response time
2. Make the exact same request again immediately
3. The second request should be much faster (cached)

Cache keys are based on:
- **Product Recommender**: `recommender:product:{user_id}:{top_k}`
- **Basket Recommender**: `recommender:basket:{product_ids_joined}:{top_n}`

---

## Troubleshooting

### OCI Authentication Errors

If you see `503 OCI service error` with authentication-related messages:

1. **Verify OCI config file exists:**
   ```bash
   ls -la ~/.oci/config
   cat ~/.oci/config
   ```

2. **Verify API key file exists and has correct permissions:**
   ```bash
   ls -la ~/.oci/oci_api_key.pem
   # Should show -rw------- (600)
   ```

3. **Check that the `key_file` path in config matches:**
   - The path in `~/.oci/config` should be `~/.oci/oci_api_key.pem` or the full absolute path

4. **Verify endpoint URLs are correct:**
   - Check `.env` file has the correct endpoint URLs
   - Ensure URLs don't include `/predict` suffix
   - Test the endpoint directly from OCI Console or using OCI CLI

### Missing Endpoint Configuration

If you see `OCI_PRODUCT_RECOMMENDER_MODEL_ENDPOINT is not configured`:

1. Check your `.env` file has the endpoint variables set
2. Restart the server after adding environment variables
3. Verify the variable names match exactly (case-sensitive)

### Connection Errors

If you see connection errors:

1. **Check server is running:**
   ```bash
   curl http://localhost:3001/api/health
   ```

2. **Check server logs** for detailed error messages:
   ```bash
   # If using npm run server:dev, check the terminal output
   # Or check logs if running in background
   ```

3. **Verify OCI endpoints are accessible:**
   - Test from OCI Console or using OCI CLI
   - Check network connectivity and firewall rules

---

## Quick Test Script

Save this as `test-recommender-apis.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:3001"

echo "Testing Product Recommender API..."
curl -X POST "${BASE_URL}/api/recommender/product" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "100773", "top_k": 5}' \
  | jq '.'

echo -e "\n\nTesting Basket Recommender API..."
curl -X POST "${BASE_URL}/api/recommender/basket" \
  -H "Content-Type: application/json" \
  -d '{"basket": ["B01CG1J7XG", "B0BKZHSDGP", "B094H5S3TY"], "top_n": 3}' \
  | jq '.'

echo -e "\n\nDone!"
```

Make it executable and run:
```bash
chmod +x test-recommender-apis.sh
./test-recommender-apis.sh
```

(Requires `jq` for JSON formatting - install with `brew install jq` on macOS)
