# Change: Add Agentic AI Flow Trigger for VIP Re-engagement

## Why
KPI #1 (Churn Risk Score) currently surfaces a recommended action card for launching a VIP re-engagement campaign, but the dashboard does not yet provide an end-to-end, one-click flow to actually trigger that campaign. We now have two key building blocks: the cohort detail API (`GET /api/kpi/churn/cohorts/VIP`) that returns user-level churn and LTV data, and an external n8n webhook that accepts a `cohort` and `users[]` payload and sends re-engagement emails. We need an integrated, agentic flow from the KPI detail modal that orchestrates these steps and clearly surfaces the outcome to the user.

## What Changes
- **New Frontend Flow (Agentic Trigger)**: Add a \"Proceed\" button to the KPI #1 detail modal (within the VIP re-engagement recommended action card) that:
  - When clicked, shows a confirmation dialog (e.g., \"Proceed to launch VIP re-engagement campaign?\") before triggering the flow.
  - Calls the cohort detail API (`GET /api/kpi/churn/cohorts/VIP?limit=3&sort=ltv&atRiskOnly=true`) to fetch the **top 3 at-risk VIP users by LTV** directly from the backend, with optional additional LTV filtering (e.g., `minLtv=5000`).
  - Optionally applies an additional client-side threshold to further refine the **at-risk VIP subset** (e.g., users with `churnProbability` ≥ the model's optimal threshold from `/api/kpi/churn/metrics`, or a default of 0.42 when unavailable).
  - Calls the external n8n webhook:
    - **URL**: `https://n8n.40b5c371.nip.io/webhook/vip-reengagement` (configurable via environment variable).
    - **Request body**:
      ```json
      {
        "cohort": "VIP",
        "users": [
          {
            "userId": "c6911ae4-2f96-43a9-bafc-90b7d2d8f391",
            "churnProbability": 0.7234,
            "ltv": 8452.50
          }
        ]
      }
      ```
  - Handles the webhook response:
    - **Response shape**: `{ "success": boolean, "message": string, "processed": number }`.
    - Displays a banner/toast/dialog in the KPI detail modal showing the `message`, with different colors/icons for `success: true` vs `success: false`.
- **UI/UX Behavior**:
  - Show loading state and disable the button while the flow is running to prevent duplicate triggers.
  - Clearly indicate how many users were processed (e.g., \"Processed 150 VIP users\") based on the `processed` field.
  - Use success styling (e.g., green/teal with check icon) when `success: true`, and error/warning styling (e.g., rose/amber with alert icon) when `success: false` or the request fails.
- **Configuration**:
  - Introduce a configurable webhook URL (e.g., `NEXT_PUBLIC_AGENTIC_FLOW_WEBHOOK_URL`) so the external endpoint is not hard-coded in the component and can later be reused for non-VIP / other campaign flows.
  - Make it easy to disable or hide the button when the webhook URL is not configured (e.g., in local environments).

## Impact
- **Modified Capability**: `kpi-dashboard` – Adds an interactive, agentic flow to the KPI #1 detail modal that connects churn analytics with an external orchestration engine (n8n) for VIP re-engagement.
- **New Behavior**:
  - The dashboard no longer just describes a VIP re-engagement campaign; it can actively trigger it and surface real execution feedback.
  - The flow leverages the existing churn API (summary, cohorts, metrics, new cohort detail endpoint) without changing backend contracts.
- **Code Touchpoints** (for future implementation):
  - `app/components/kpi-detail-modal/kpi-detail-modal.tsx` – Add button and UI states for the VIP re-engagement action card.
  - `app/lib/api/churn-api.ts` – (Optional) Add a small helper for calling the cohort detail API and external webhook, or reuse existing fetch utilities.
  - Environment configuration (`.env`, `.env.example`) – Add webhook URL configuration and documentation.
- **Backend Spec Enhancement**:
  - The `churn-model-api` capability is extended to support additional filters on the cohort detail endpoint:
    - `atRiskOnly=true|false` to restrict the `users` list to at-risk customers only.
    - `minLtv` / `maxLtv` to restrict the `users` list to users within a specific LTV range.
  - These filters affect only the `users` array; summary metrics (`summary.customerCount`, `summary.atRiskCount`, `pagination.total`) continue to reflect the full cohort.

## Example Requests & Responses

### External Webhook Request (VIP Re-engagement)

**Request**

```http
POST https://n8n.40b5c371.nip.io/webhook/vip-reengagement
Content-Type: application/json

{
  "cohort": "VIP",
  "users": [
    {
      "userId": "c6911ae4-2f96-43a9-bafc-90b7d2d8f391",
      "churnProbability": 0.7234,
      "ltv": 8452.50
    },
    {
      "userId": "2cdbc0df-3d63-47be-8a2f-19c5b4ee2b59",
      "churnProbability": 0.6891,
      "ltv": 6200.00
    }
  ]
}
```

**Response**

```json
{
  "success": true,
  "message": "VIP re-engagement emails have been sent.",
  "processed": 2
}
```

### Example UI Behavior

- **Success case**:
  - Banner at top of KPI detail modal:
    - Icon: ✓ (check)
    - Color: Green/teal background with dark text
    - Text: \"VIP re-engagement emails have been sent. (Processed 150 VIP customers)\"
- **Failure case**:
  - Banner:
    - Icon: ! (alert)
    - Color: Rose/amber background
    - Text: e.g., \"VIP re-engagement flow failed: n8n endpoint unavailable\" or the `message` returned by the webhook.

