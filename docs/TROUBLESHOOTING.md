# Troubleshooting Guide

This guide lists common issues encountered when running the churn ML demo and how to resolve them.

## 1. Oracle Client / Wallet Issues

### 1.1 ORA-12154 / ORA-12541 / ORA-01017

See `docs/ADB_SETUP.md` for full details. Quick checks:

- Verify `ADB_WALLET_PATH` points to the extracted wallet directory.
- Ensure `TNS_ADMIN` is set to the same wallet directory.
- Confirm `ADB_CONNECTION_STRING` matches an alias from `tnsnames.ora`.
- Double-check `ADB_USERNAME` and `ADB_PASSWORD` (try logging in via SQL Developer).

### 1.2 "Oracle Client library not found"

- Make sure Oracle Instant Client is installed (see `docs/ADB_SETUP.md`).
- On macOS: `brew install instantclient-basic instantclient-sdk`.
- On Linux: install the Instant Client RPMs.
- Ensure the client library directory is discoverable:
  - `LD_LIBRARY_PATH` (Linux) or `DYLD_LIBRARY_PATH` (macOS).

## 2. Next.js + oracledb Issues

See `docs/NEXTJS_ORACLE_WORKAROUNDS.md` for detailed analysis.

Quick summary:

- Next.js 16 + Node.js 22 require using `serverExternalPackages: ["oracledb"]` in `next.config.ts`.
- For local thick-mode issues in Next.js, prefer routing backend calls through the **Express server** on port 3001.

## 3. Express Server Issues

### 3.1 Server does not start / pool initialization fails

- Check the Express logs (terminal running `npm run server:dev`) for:
  - `[Oracle Init]` messages.
  - Any ORA- errors or wallet path problems.
- Verify:
  - `ADB_WALLET_PATH` and `TNS_ADMIN` are set.
  - Wallet files exist at the configured path.

### 3.2 Swagger UI not available

- Confirm `swagger-ui-express` is installed:
  ```bash
  npm install swagger-ui-express
  ```
- Ensure the Express server is running:
  ```bash
  npm run server:dev
  ```
- Open `http://localhost:3001/api-docs` in your browser.

## 4. Frontend / API Call Issues

### 4.1 Multiple API calls on first load

- React StrictMode in development intentionally double-mounts components.
- We mitigate this with:
  - In-flight promise coalescing in `app/lib/api/churn-api.ts`.
  - Caching in `app/data/kpis/index.ts`.
  - Per-component guards in `app/page.tsx`.
- In production (`npm run build && npm run start`), you should see one clean batch of 5 calls on first load.

### 4.2 KPI #1 modal shows fallback data

- Check browser console logs for `[KPI1] Failed to fetch churn data from API`.
- Verify Express server and ADB are running.
- Use Swagger UI or `scripts/test-api-endpoints.sh` to confirm all churn endpoints return `200`.

## 5. ML Pipeline Issues

### 5.1 Validation failures in `validate_churn_data.py`

- Row count section is informational; focus on:
  - `Data Types`
  - `Constraints`
  - `User Id Mapping`
- If `User Id Mapping` fails:
  - Ensure all `ADMIN.USERS.ID` values have corresponding `OML.USER_PROFILES.USER_ID`.
  - Re-run `scripts/map_dataset_to_users.py` if necessary.

### 5.2 Poor model performance

- Check `validate_model_performance.py` output:
  - AUC should be > 0.70 (currently ~0.93).
- If AUC drops:
  - Verify feature views and training data counts with `validate_churn_data.py`.
  - Re-run the full pipeline:
    ```bash
    python scripts/validate_churn_data.py
    python scripts/validate_model_performance.py
    python scripts/local/test_pipeline_end_to_end.py
    ```

## 6. Where to Look Next

- **Setup & ADB**: `SETUP.md`, `docs/ADB_SETUP.md`
- **API behavior**: `docs/CHURN_API_REFERENCE.md`, Swagger UI at `/api-docs`
- **ML pipeline**: `docs/ML_PIPELINE_USAGE.md`
- **Dataset & risk factors**: `docs/DATASET_SOURCE_AND_PREP.md`, `docs/RISK_FACTORS_*`
- **OCI deployment**: `docs/OCI_DEPLOYMENT_NOTES.md`

