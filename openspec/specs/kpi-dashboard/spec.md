# kpi-dashboard Specification

## Purpose
TBD - created by archiving change add-kpi-detail-pages. Update Purpose after archive.
## Requirements
### Requirement: KPI Detail Modal System
The system SHALL provide detailed modal views for each of the 10 Leading AI/ML KPIs designed for B2C Fashion E-commerce executives (CFO, COO, CMO). These KPIs are forward-looking, predictive indicators (30-90 days ahead) that enable proactive decision-making. Each modal SHALL display comprehensive analysis including key metrics, visualizations, data tables, AI model information, recommended actions, and business impact summaries.

Each KPI SHALL display:
- Prediction horizon (3-180 days depending on KPI)
- Executive owner(s) (CFO/COO/CMO) with role-specific context
- Forward-looking forecasts (not just historical data)
- Quantified business impact ranges
- Root cause analysis for predictive signals

**Note**: For KPI #1 (Churn Risk Score), metrics and visualizations SHALL be populated from REST API endpoints when available, with static synthetic data as fallback.

#### Scenario: Open KPI detail modal from dashboard
- **WHEN** user clicks on a KPI card or "View Details" button on the main dashboard
- **THEN** a modal overlay appears with the KPI detail page
- **AND** the modal displays the KPI number badge, title, owner badges, and prediction horizon in the header
- **AND** the modal body contains all required sections (metrics grid, chart, data table, AI info, actions, impact)
- **AND** for KPI #1, if API is available, data is fetched from churn API endpoints; otherwise static data is used

### Requirement: Modal Header
Each KPI detail modal SHALL include a header section with:
- KPI number badge (e.g., "KPI #1")
- KPI title
- Owner badges (CFO / COO / CMO)
- Prediction horizon badge (e.g., "60-90 Days")
- Close button

The header SHALL be sticky (remain visible when scrolling modal content).

#### Scenario: Modal header displays correctly
- **WHEN** a KPI detail modal is opened
- **THEN** the header shows all required elements in the specified order
- **AND** the header remains visible when scrolling through modal content

### Requirement: Key Metrics Grid
Each KPI detail modal SHALL display a grid of 4-6 metric cards showing:
- Primary value with trend indicator (↑/↓/→)
- Secondary value with trend indicator
- Tertiary value (if applicable)
- Model confidence score with visual progress bar

Metric values SHALL use monospace font for numbers. Trend indicators SHALL use color coding (Green for positive, Rose for negative, Amber for neutral/warning).

#### Scenario: Metrics grid displays key indicators
- **WHEN** a KPI detail modal is opened
- **THEN** the metrics grid displays 4-6 metric cards with values, trends, and confidence scores
- **AND** numeric values use monospace font
- **AND** trend indicators use appropriate colors

### Requirement: Main Visualization Chart
Each KPI detail modal SHALL include a main visualization chart (300-400px height) using Chart.js. The chart type SHALL be context-specific per KPI:
- KPI #1: Stacked area chart (churn risk distribution)
- KPI #2: Horizontal bar chart (SKUs by stockout probability)
- KPI #3: Price-demand elasticity curve
- KPI #4: Multi-line chart (payback trends by channel)
- KPI #5: Bar chart (return rate by category)
- KPI #6: Dual-axis line chart (email engagement decay)
- KPI #7: Supplier performance heatmap/bar chart
- KPI #8: Real-time line chart with control bands
- KPI #9: CLV distribution chart
- KPI #10: Forecast chart with confidence intervals

Charts SHALL include interactive tooltips with detailed values, legends, and axis labels. Charts SHALL be responsive and maintain aspect ratio.

#### Scenario: Chart displays with correct data
- **WHEN** a KPI detail modal is opened
- **THEN** the main visualization chart displays with the correct chart type for that KPI
- **AND** the chart shows accurate data from synthetic data sources
- **AND** tooltips display detailed values on hover
- **AND** the chart is properly sized (300-400px height)

### Requirement: Data Table
Each KPI detail modal SHALL include a drill-down data table with:
- Sortable columns
- Color-coded risk indicators (Green/Amber/Rose)
- Action status column (where applicable)
- Pagination or scroll for tables with many rows (max 10 rows visible)

Table rows SHALL be hoverable and clickable for additional detail (if applicable).

#### Scenario: Data table displays and sorts correctly
- **WHEN** a KPI detail modal is opened
- **THEN** the data table displays relevant drill-down data
- **AND** columns are sortable by clicking headers
- **AND** risk indicators use appropriate color coding
- **AND** tables with >10 rows show pagination or scroll

### Requirement: AI Model Information
Each KPI detail modal SHALL display AI model information including:
- Model type (e.g., "XGBoost Binary Classification")
- Training data description (e.g., "24 months transaction data")
- Confidence level with explanation
- Last model update timestamp
- Data sources list

#### Scenario: AI model information displays
- **WHEN** a KPI detail modal is opened
- **THEN** the AI model information section displays all required fields
- **AND** the confidence level is clearly indicated
- **AND** the last update timestamp is shown

### Requirement: Recommended Actions
Each KPI detail modal SHALL display a list of recommended actions in priority order. Each action SHALL include:
- Action title and description
- Priority level (High/Medium/Low) with color coding
- Expected outcome
- Owner assignment (CMO/COO/CFO)
- Due date or urgency indicator

Actions SHALL be displayed as cards with visual priority indicators (border color, icon).

#### Scenario: Recommended actions display with priority
- **WHEN** a KPI detail modal is opened
- **THEN** recommended actions are displayed in priority order
- **AND** each action shows title, description, priority, owner, and due date
- **AND** priority is visually indicated with color coding

### Requirement: Business Impact Summary
Each KPI detail modal SHALL display a business impact summary including:
- Revenue impact (positive/negative)
- Cost impact
- ROI if action taken (where applicable)

Impact values SHALL be clearly labeled and use appropriate formatting (currency, percentages).

#### Scenario: Business impact summary displays
- **WHEN** a KPI detail modal is opened
- **THEN** the business impact summary displays revenue impact, cost impact, and ROI
- **AND** values are properly formatted (currency symbols, percentages)

### Requirement: Synthetic Data Generation
The system SHALL generate realistic synthetic data for a B2C fashion e-commerce company with:
- $200M annual revenue
- ~500,000 active customers
- ~15,000 active SKUs
- ~1.2M orders/year
- Average Order Value (AOV): $85-120

Synthetic data SHALL match the specifications provided for each KPI, including cohort data, SKU information, channel performance, and forecast values.

#### Scenario: Synthetic data matches specifications
- **WHEN** KPI detail modals are opened
- **THEN** all displayed data matches the synthetic data requirements from the specifications
- **AND** values are realistic for a $200M B2C fashion e-commerce company
- **AND** data relationships are consistent (e.g., LTV calculations, revenue forecasts)

### Requirement: Responsive Design
KPI detail modals SHALL be responsive:
- Desktop: Max-width 1000px, centered
- Mobile: Single-column layout, collapsible sections
- Touch-friendly table scrolling on mobile
- Swipeable charts on mobile (if applicable)

#### Scenario: Modal displays correctly on mobile
- **WHEN** a KPI detail modal is opened on a mobile device
- **THEN** the layout adapts to single-column
- **AND** sections are collapsible for easier navigation
- **AND** tables are scrollable with touch gestures

### Requirement: Modal Animations
KPI detail modals SHALL include animations:
- Fade-in animation when modal opens
- Staggered reveal animation for modal sections
- Smooth transitions for chart rendering

Animations SHALL respect user preferences (reduce motion).

#### Scenario: Modal animates on open
- **WHEN** a KPI detail modal is opened
- **THEN** the modal fades in smoothly
- **AND** sections appear with staggered reveal animation
- **AND** charts render with smooth transitions

### Requirement: Color Coding System
The system SHALL use a consistent color coding system:
- Green/Emerald: Good status, positive trends, low risk
- Amber/Yellow: Warning status, neutral trends, medium risk
- Rose/Red: Critical status, negative trends, high risk
- Teal: Information, confidence indicators
- Violet: Prediction horizon badges

#### Scenario: Color coding is consistent
- **WHEN** viewing any KPI detail modal
- **THEN** color coding follows the specified system
- **AND** risk indicators, trend arrows, and status badges use appropriate colors

### Requirement: KPI Data Source
The system SHALL fetch KPI #1 (Churn Risk Score) data from REST API endpoints, with fallback to static synthetic data if API is unavailable.

KPI #1 data SHALL be fetched from:
- Primary: `GET /api/kpi/churn/summary` for summary metrics
- Primary: `GET /api/kpi/churn/cohorts` for cohort breakdown
- Primary: `GET /api/kpi/churn/metrics` for model information
- Primary: `GET /api/kpi/churn/chart-data` for visualization data
- Fallback: Static data from `app/data/synthetic/kpi1-churn-risk.ts`

#### Scenario: Load KPI #1 from API
- **WHEN** dashboard loads or KPI #1 is viewed
- **THEN** frontend attempts to fetch data from API endpoints
- **AND** if API responds successfully, frontend uses API data
- **AND** if API fails or times out, frontend uses static fallback data
- **AND** loading states are displayed during API calls

#### Scenario: Handle API errors gracefully
- **WHEN** API request fails (network error, 500, timeout)
- **THEN** frontend logs error and uses static fallback data
- **AND** user sees KPI data (from fallback) without error disruption
- **AND** error is logged for debugging purposes

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

