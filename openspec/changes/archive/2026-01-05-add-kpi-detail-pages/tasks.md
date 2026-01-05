## 1. Setup and Infrastructure
- [x] 1.1 Install Chart.js and React Chart.js wrapper (`chart.js`, `react-chartjs-2`)
- [x] 1.2 Create base modal component structure (`app/components/kpi-detail-modal.tsx`)
- [x] 1.3 Set up modal overlay and backdrop with animations
- [x] 1.4 Create modal header component with KPI badge, title, owner badges, horizon badge, close button
- [x] 1.5 Implement sticky header functionality for scrollable modal body

## 2. Core Modal Sections
- [x] 2.1 Create key metrics grid component (4-6 metric cards with values, trends, colors)
- [x] 2.2 Create main visualization section with Chart.js integration
- [x] 2.3 Create data table component with sortable columns, risk indicators, pagination (basic table implemented, sorting to be enhanced)
- [x] 2.4 Create AI model information section (display model metadata: model type, training data description, confidence scores, data sources) - static display only, no actual ML inference
- [x] 2.5 Create recommended actions section (priority-ordered cards with owner, due date, impact)
- [x] 2.6 Create business impact summary section (revenue impact, cost impact, ROI)

## 3. Chart Components
- [x] 3.1 Create reusable chart wrapper component with Chart.js configuration
- [x] 3.2 Implement stacked area chart for churn risk (KPI #1)
- [x] 3.3 Implement horizontal bar chart for stockout risk (KPI #2)
- [ ] 3.4 Implement price-demand elasticity curve (KPI #3)
- [ ] 3.5 Implement multi-line chart for CAC payback trends (KPI #4)
- [ ] 3.6 Implement bar chart for return rate by category (KPI #5)
- [ ] 3.7 Implement dual-axis line chart for email engagement decay (KPI #6)
- [ ] 3.8 Implement supplier performance heatmap/bar chart (KPI #7)
- [ ] 3.9 Implement real-time line chart with control bands (KPI #8)
- [ ] 3.10 Implement CLV distribution chart (KPI #9)
- [ ] 3.11 Implement forecast chart with confidence intervals (KPI #10)

## 4. Data Layer (Synthetic Data - No ML Implementation)
- [x] 4.1 Create TypeScript data files/constants for B2C fashion e-commerce synthetic data
- [x] 4.2 Create static data for KPI #1 (Churn Risk): cohorts, risk scores, LTV at risk (pre-calculated values)
- [x] 4.3 Create static data for KPI #2 (Stockout Risk): SKUs, inventory levels, lead times (pre-calculated values)
- [ ] 4.4 Create static data for KPI #3 (Price Elasticity): price points, demand curves, scenarios (pre-calculated values)
- [ ] 4.5 Create static data for KPI #4 (CAC Payback): channel performance, payback periods (pre-calculated values)
- [ ] 4.6 Create static data for KPI #5 (Return Rate): product categories, return reasons, simulated NLP signals (pre-calculated values)
- [ ] 4.7 Create static data for KPI #6 (Email Decay): subscriber cohorts, engagement trends (pre-calculated values)
- [ ] 4.8 Create static data for KPI #7 (Supply Chain Risk): supplier performance, delay probabilities (pre-calculated values)
- [ ] 4.9 Create static data for KPI #8 (Conversion Anomaly): CVR trends, anomaly history (pre-calculated values)
- [ ] 4.10 Create static data for KPI #9 (CLV Trajectory): cohort CLV, channel performance (pre-calculated values)
- [ ] 4.11 Create static data for KPI #10 (Demand Forecast): revenue forecasts, category breakdowns (pre-calculated values)
- [ ] 4.12 Create AI model metadata objects (model type, confidence, training data description) - static information only

## 5. KPI-Specific Modal Content
- [x] 5.1 Implement KPI #1 modal: Churn Risk Score with cohort breakdown
- [x] 5.2 Implement KPI #2 modal: Stockout Risk with SKU-level details
- [ ] 5.3 Implement KPI #3 modal: Price Elasticity with scenario simulator
- [ ] 5.4 Implement KPI #4 modal: CAC Payback with channel analysis
- [ ] 5.5 Implement KPI #5 modal: Return Rate Predictor with product flags
- [ ] 5.6 Implement KPI #6 modal: Email Engagement Decay with cohort analysis
- [ ] 5.7 Implement KPI #7 modal: Supply Chain Lead Time Risk with supplier assessment
- [ ] 5.8 Implement KPI #8 modal: Conversion Anomaly Detector with real-time monitoring
- [ ] 5.9 Implement KPI #9 modal: Customer CLV Trajectory with cohort analysis
- [ ] 5.10 Implement KPI #10 modal: Demand Forecast with confidence intervals

## 6. UI/UX Enhancements
- [x] 6.1 Implement color coding system (Green/Amber/Rose for risk levels)
- [x] 6.2 Add fade-in animations for modal appearance
- [ ] 6.3 Add staggered reveal animations for modal sections
- [x] 6.4 Implement responsive design (mobile: single-column, collapsible sections)
- [ ] 6.5 Add loading states for data refresh simulation
- [ ] 6.6 Add "Last Updated" timestamps and data freshness indicators
- [x] 6.7 Implement monospace font for numeric values
- [x] 6.8 Add interactive chart tooltips with detailed values

## 7. Integration
- [x] 7.1 Connect modal open/close to main dashboard KPI cards
- [x] 7.2 Pass KPI ID and data to modal component
- [x] 7.3 Implement keyboard navigation (ESC to close)
- [x] 7.4 Implement click-outside-to-close functionality
- [x] 7.5 Add modal state management (open/close, current KPI)

## 8. Testing and Polish
- [ ] 8.1 Test all 10 KPI modals render correctly
- [ ] 8.2 Verify charts display with correct data and styling
- [ ] 8.3 Test responsive behavior on mobile devices
- [ ] 8.4 Verify accessibility (keyboard navigation, ARIA labels)
- [ ] 8.5 Test modal animations and transitions
- [ ] 8.6 Verify synthetic data matches specification requirements (realistic values, proper relationships)
- [ ] 8.7 Test table sorting and pagination functionality
- [ ] 8.8 Verify all interactions work (click to open modal, close modal, sort tables, hover tooltips)
- [ ] 8.9 Ensure demo is fully clickable and navigable without any backend or ML dependencies

