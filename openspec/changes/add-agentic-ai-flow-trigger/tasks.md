# Implementation Tasks

## 1. UI Integration (KPI Detail Modal)
- [x] 1.1 Identify the VIP re-engagement recommended action card in `KPIDetailModal` (KPI #1).
- [x] 1.2 Add a \"Proceed\" button to that card (visible only when `metadata.id === 1` and webhook URL is configured).
- [x] 1.3 When the user clicks \"Proceed\", show a confirmation dialog (e.g., \"Proceed to launch VIP re-engagement campaign?\") before triggering the flow.
- [x] 1.4 Add loading/disabled states to the button while the agentic flow is in progress.
- [x] 1.5 Ensure the button is keyboard accessible and announced to screen readers (ARIA attributes).

## 2. Data Orchestration (Agentic Flow)
- [x] 2.1 Implement a client-side function to fetch VIP cohort details using the existing cohort detail API:
  - `GET /api/kpi/churn/cohorts/VIP?limit=3&sort=ltv&atRiskOnly=true`
- [x] 2.2 Implement logic to derive **at-risk VIP users** from the cohort detail response:
  - Prefer using the optimal threshold from `/api/kpi/churn/metrics` when available.
  - Fallback to a default threshold (e.g., 0.42) if metrics are unavailable.
  - Filter users where `churnProbability >= threshold`.
- [x] 2.3 Construct the external webhook payload:
  - `cohort`: \"VIP\"
  - `users`: filtered list of `{ userId, churnProbability, ltv }`.
- [x] 2.4 Implement a helper for calling the n8n webhook using `fetch`:
  - URL from environment configuration (e.g., `NEXT_PUBLIC_AGENTIC_FLOW_WEBHOOK_URL`).
  - POST JSON body exactly matching the required shape.
- [x] 2.5 Handle non-200 responses and JSON parse errors gracefully.

## 3. Response Handling & UI Feedback
- [x] 3.1 Parse webhook response `{ success, message, processed }`.
- [x] 3.2 Display a banner/toast/dialog inside the KPI detail modal:
  - Show the `message` string.
  - If `processed` is present, append summary (e.g., \"Processed 150 VIP customers\").
- [x] 3.3 Use different visuals based on `success`:
  - `success === true`: green/teal styling with check icon.
  - `success === false` or network error: rose/amber styling with alert icon.
- [x] 3.4 Ensure the banner/toast is dismissible and non-blocking.
- [x] 3.5 Reset button state after the flow completes (both success and error).

## 4. Configuration & Environment
- [x] 4.1 Add a new environment variable for the webhook URL (e.g., `NEXT_PUBLIC_AGENTIC_FLOW_WEBHOOK_URL`) to:
  - `.env.example` (local development / generic docs)
  - `.env.oci` (OCI VM Podman deployment)
  - Documentation (e.g., `README.md` or a dedicated integration doc).
- [x] 4.2 In the frontend, read the webhook URL from `process.env.NEXT_PUBLIC_AGENTIC_FLOW_WEBHOOK_URL`.
- [x] 4.3 Hide or disable the \"Proceed\" button when the webhook URL is not configured.
- [ ] 4.4 Document how to configure the webhook URL and any required authentication (if added later).

## 5. Error Handling & Edge Cases
- [x] 5.1 Handle the case where the VIP cohort API call fails:
  - Show an error banner indicating cohort data could not be loaded.
  - Do not call the external webhook.
- [x] 5.2 Handle the case where there are **no at-risk VIP users** after filtering:
  - Show an informational banner (e.g., \"No at-risk VIP customers to re-engage at this time.\").
  - Skip calling the webhook.
- [x] 5.3 Handle network errors/timeouts when calling the webhook:
  - Show an error banner with a generic failure message.
  - Optionally include a \"Try again\" action.
- [x] 5.4 Prevent double-submission:
  - Disable the button while a request is in-flight.
  - Ignore clicks while the agentic flow is running.

## 6. Testing
- [ ] 6.1 Test happy path:
  - VIP cohort API returns data.
  - Webhook responds with `{ success: true, message, processed }`.
  - Banner shows success message and processed count.
- [ ] 6.2 Test invalid/empty VIP cohort:
  - VIP cohort API returns 200 but no users or no at-risk users.
  - Banner shows appropriate informational message.
- [ ] 6.3 Test VIP cohort API failure:
  - Simulate 500/503 or network error from `/api/kpi/churn/cohorts/VIP`.
  - Verify error banner and no webhook call.
- [ ] 6.4 Test webhook failure:
  - Simulate non-200 response from webhook.
  - Simulate `success: false` in response.
  - Verify error/warning banner with correct styling.
- [ ] 6.5 Test missing webhook URL:
  - Remove `NEXT_PUBLIC_AGENTIC_FLOW_WEBHOOK_URL` from env.
  - Verify button is hidden or disabled, and no calls are attempted.
- [ ] 6.6 Test accessibility:
  - Verify button is focusable and labeled.
  - Verify banner is announced to screen readers (ARIA live region).

## 7. API Documentation (Swagger / OpenAPI)
- [x] 7.1 Update the OpenAPI spec in `server/openapi.ts` for the cohort detail endpoint (`/api/kpi/churn/cohorts/{name}`) to reflect:
  - `limit` default = 3 (example: 3).
  - New query parameters: `atRiskOnly` (default: true), `minLtv`, `maxLtv` with validation rules.
  - Updated response examples where `pagination.limit` reflects the new default of 3.
- [x] 7.2 Verify that Swagger UI (`/api-docs`) shows the new query parameters and default values, and that the "Try it out" feature uses them correctly.

