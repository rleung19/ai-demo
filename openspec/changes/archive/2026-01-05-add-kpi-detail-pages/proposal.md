# Change: Add KPI Detail Pages

## Why
The AI/ML Executive Dashboard needs comprehensive drill-down views for each of the 10 Leading AI/ML KPIs designed for B2C Fashion E-commerce executives (CFO, COO, CMO). These KPIs are **forward-looking, predictive indicators** (30-90 days ahead) that enable proactive decision-making before business outcomes materialize. Currently, the dashboard shows high-level KPI cards, but executives need detailed analysis, actionable insights, and recommended interventions for each KPI.

**Phase 1 Scope: Clickable Demo**
This first iteration focuses on creating a fully interactive, clickable demo with synthetic data. The implementation will:
- Display realistic KPI data using pre-generated synthetic datasets (no actual ML model training or inference)
- Show AI model information as metadata (model types, confidence scores, training data descriptions) without running actual models
- Demonstrate the UI/UX and user flows for all 10 KPIs
- Enable stakeholders to interact with and evaluate the dashboard design before ML implementation

The detailed KPI analysis document (`detailed-kpi-analysis.md`) establishes that these KPIs are:
- Predictive of business outcomes before they materialize
- Actionable by CFO, COO, or CMO teams with clear decision authority
- Implementable using AI/Machine Learning techniques (to be implemented in future phases)
- Relevant to B2C fashion e-commerce unit economics ($200M revenue, 500K customers, 15K SKUs)
- Separated by executive role and decision authority

Each KPI detail page must show not just current metrics, but predictive forecasts, root cause analysis, intervention recommendations, and quantified business impact to enable executives to take action while there's still time to influence outcomes.

## What Changes
- **ADDED**: KPI detail modal system with consistent structure across all 10 KPIs
- **ADDED**: Key metrics grid (4-6 metric cards) with trend indicators
- **ADDED**: Main visualization charts using Chart.js (context-specific per KPI)
- **ADDED**: Drill-down data tables with sortable columns and risk indicators
- **ADDED**: AI model information section displaying model metadata (model type, training data description, confidence scores, data sources) - displayed as static information for demo purposes
- **ADDED**: Recommended actions section with priority-ordered action cards
- **ADDED**: Business impact summary with revenue/cost/ROI calculations
- **ADDED**: Pre-generated synthetic data for realistic B2C fashion e-commerce scenarios ($200M revenue, 500K customers, 15K SKUs) - static datasets that simulate ML predictions without actual model inference
- **ADDED**: Modal header with KPI number badge, title, owner badges, prediction horizon, and close button
- **ADDED**: Responsive modal design (max-width 1000px, scrollable, sticky header)
- **ADDED**: Color-coded risk indicators (Green/Amber/Rose) and status badges
- **ADDED**: Interactive chart tooltips and time period selectors where applicable

## The 10 Leading AI/ML KPIs

1. **KPI #1: Predictive Churn Risk Score (Cohort-Level)** - CMO/COO, 60-90 days, XGBoost classification
2. **KPI #2: Inventory Stockout Risk Probability** - COO/CFO, 14-28 days, Time series forecasting
3. **KPI #3: Dynamic Price Elasticity & Revenue Impact Forecast** - CFO/CMO, 7-14 days, Price optimization regression
4. **KPI #4: CAC Payback Period Trend** - CFO/CMO, 30-60 days, Cohort analysis with curve-fitting
5. **KPI #5: Return Rate Trend & Predictive Return Drivers** - COO/CMO, 10-21 days, NLP sentiment analysis
6. **KPI #6: Email Engagement Decay Index** - CMO/COO, 14-30 days, Time series anomaly detection
7. **KPI #7: Supply Chain Lead Time Risk Index** - COO/CFO, 14-42 days, Time series + external data integration
8. **KPI #8: Conversion Rate Anomaly & Root Cause Detection** - CMO/COO, 3-7 days, Statistical process control
9. **KPI #9: Customer Lifetime Value (CLV) Trajectory by Cohort** - CFO/CMO, 90-180 days, Predictive regression
10. **KPI #10: Demand Forecast Accuracy + Auto-Correction Alert** - CFO/COO, 14-42 days, Time series (Prophet, LSTM)

Each KPI has specific AI/ML techniques, quantified business impacts, and executive ownership as documented in `detailed-kpi-analysis.md`.

## Impact
- **Affected specs**: New capability `kpi-dashboard`
- **Affected code**: 
  - New modal component system (`app/components/kpi-detail-modal.tsx`)
  - Chart components (`app/components/charts/`)
  - Data table components (`app/components/data-tables/`)
  - KPI-specific data and configurations (`app/data/kpis/`)
  - Pre-generated synthetic data files (`app/data/synthetic/`) - static JSON/TypeScript data files
- **Dependencies**: Chart.js v4+ for visualizations
- **UI/UX**: Modal-based detail views accessible from main dashboard KPI cards
- **Phase 1 Scope**: Frontend-only implementation with synthetic data (no ML model training, inference, or API calls)
- **Business Context**: 
  - Industry: B2C Fashion, Cosmetics & Accessories (similar to ASOS, NET-A-PORTER)
  - Target Users: CFO, COO, CMO executives
  - Prediction Horizons: 3-180 days ahead depending on KPI
  - Quantified Impacts: Each KPI has documented business impact ranges (e.g., 8-12% churn reduction, $60K-150K emergency freight savings, 5-15% revenue lift from pricing optimization)
- **Reference Documents**: 
  - `mnt_kpi-detail-page-specifications.md` - Detailed UI/UX specifications
  - `detailed-kpi-analysis.md` - Business context, AI/ML techniques, and quantified impacts

