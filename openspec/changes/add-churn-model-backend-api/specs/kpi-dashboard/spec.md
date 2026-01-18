# kpi-dashboard Specification

## MODIFIED Requirements

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

### Requirement: KPI Detail Modal
Each KPI detail modal SHALL display comprehensive analysis including key metrics, visualizations, data tables, AI model information, recommended actions, and business impact summaries.

**Note**: For KPI #1, metrics and visualizations SHALL be populated from API endpoints when available, with static data as fallback.

#### Scenario: Open KPI #1 detail modal with API data
- **WHEN** user clicks on KPI #1 card
- **THEN** frontend fetches data from churn API endpoints
- **AND** modal displays real-time metrics from API
- **AND** charts render with API data
- **AND** if API unavailable, modal displays static data with indicator
