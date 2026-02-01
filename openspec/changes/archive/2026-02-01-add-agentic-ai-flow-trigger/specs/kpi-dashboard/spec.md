## ADDED Requirements

### Requirement: Agentic VIP Re-engagement Flow Trigger
The system SHALL provide an agentic flow trigger in the KPI #1 (Churn Risk Score) detail modal that allows the user to launch a VIP re-engagement campaign via an external orchestration service (n8n) using churn model outputs.

The VIP re-engagement trigger SHALL:
- Be rendered as a primary action button in the **VIP re-engagement** recommended action card within the KPI #1 detail modal.
- Only be visible when KPI #1 is active and a VIP cohort is available.
- Use the existing cohort detail API (`GET /api/kpi/churn/cohorts/VIP?limit=3&sort=ltv&atRiskOnly=true`) to obtain the **top 3 at-risk VIP users by LTV** from the backend.
- Optionally refine the **at-risk VIP subset** further based on churn probability, preferably using the model's optimal threshold from the churn metrics endpoint.
- Call an external HTTP endpoint (n8n webhook) with the cohort name and array of at-risk VIP users.
- Display a clear success or failure message in the modal after the flow completes.

#### Scenario: Launch VIP re-engagement campaign (success)
- **WHEN** the user opens the KPI #1 detail modal
- **AND** the modal displays a recommended action card with a primary \"Proceed\" button for the VIP re-engagement campaign
- **AND** the user clicks the \"Proceed\" button
- **AND** the system shows a confirmation dialog (e.g., \"Proceed to launch VIP re-engagement campaign?\")
- **AND** the user confirms the dialog (e.g., clicks \"Proceed\" in the dialog)
- **THEN** the system fetches VIP cohort details from `GET /api/kpi/churn/cohorts/VIP?limit=3&sort=ltv&atRiskOnly=true`
- **AND** the system may optionally further refine at-risk VIP users by filtering on churn probability (e.g., `churnProbability >= optimalThreshold` obtained from `/api/kpi/churn/metrics`, or a documented default threshold if unavailable)
- **AND** the system calls the external webhook endpoint (configured via environment variable) with body:
  - `cohort`: \"VIP\"
  - `users`: array of `{ userId, churnProbability, ltv }` for at-risk VIP users
- **AND** the webhook responds with `{ \"success\": true, \"message\": \"VIP re-engagement emails have been sent.\", \"processed\": 2 }` (or similar)
- **AND** the modal displays a success banner/toast with:
  - A success icon
  - Green/teal styling
  - The `message` from the response and the `processed` count (e.g., \"VIP re-engagement emails have been sent. Processed 150 VIP customers.\")

#### Scenario: No at-risk VIP users
- **WHEN** the user clicks the \"Proceed\" button and confirms the dialog
- **AND** the system fetches VIP cohort details successfully
- **AND** after applying the at-risk filter, there are zero VIP users to re-engage
- **THEN** the system SHALL NOT call the external webhook
- **AND** the modal displays an informational banner (e.g., \"No at-risk VIP customers to re-engage at this time.\")

#### Scenario: External webhook failure
- **WHEN** the user clicks the \"Proceed\" button and confirms the dialog
- **AND** the system calls the external webhook with the correct payload
- **AND** the webhook responds with `success: false` or a non-200 HTTP status code
- **THEN** the modal displays an error banner/toast with:
  - An error/warning icon
  - Rose/amber styling
  - A clear error message (e.g., \"VIP re-engagement flow failed: n8n endpoint unavailable\" or the `message` field from the response)
- **AND** the trigger button state is reset so the user can try again if appropriate.

#### Scenario: VIP cohort API failure
- **WHEN** the user clicks the \"Proceed\" button and confirms the dialog
- **AND** the VIP cohort detail API (`GET /api/kpi/churn/cohorts/VIP`) fails (network error, 5xx, or timeout)
- **THEN** the system SHALL NOT call the external webhook
- **AND** the modal displays an error banner indicating that VIP cohort data could not be loaded
- **AND** the user sees a clear, non-technical message explaining that the re-engagement flow could not be started.

#### Scenario: Button states and accessibility
- **WHEN** the user clicks the \"Proceed\" button and confirms the dialog
- **THEN** the button becomes disabled and shows a loading indicator while the agentic flow is in progress
- **AND** subsequent clicks are ignored until the current flow completes
- **AND** the success/error banner is announced to screen readers (ARIA live region) and can be dismissed
- **AND** keyboard users can focus and activate the button and dismiss the banner using standard keyboard interactions.

