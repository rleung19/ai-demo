# kpi-dashboard Specification

## ADDED Requirements

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

## MODIFIED Requirements

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
