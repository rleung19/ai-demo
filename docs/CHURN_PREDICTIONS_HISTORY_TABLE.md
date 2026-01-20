# CHURN_PREDICTIONS_HISTORY Table Design

## Table Name

**`OML.CHURN_PREDICTIONS_HISTORY`**

## Purpose

Store **historical churn predictions** for trend analysis and time-series charts. This table contains:
- Weekly snapshots of predictions
- Used for calculating trends ("↑ 12 from last week")
- Used for 7-week historical charts
- Enables comparison of current vs. historical metrics

## Key Characteristics

- **Rows**: Multiple per user (one per snapshot/week)
- **USER_ID**: Real UUIDs from `ADMIN.USERS.ID`
- **SNAPSHOT_DATE**: Weekly snapshots (e.g., every Monday)
- **Retention**: Keep last 8-12 weeks (configurable)
- **Purpose**: Historical tracking for trend analysis

## Table Schema

| Column | Data Type | Description |
|--------|-----------|-------------|
| `USER_ID` | VARCHAR2(36) | Foreign key to ADMIN.USERS.ID |
| `SNAPSHOT_DATE` | DATE | Date of prediction snapshot (weekly) |
| `PREDICTED_CHURN_PROBABILITY` | NUMBER(5,4) | Churn probability (0.0 to 1.0) |
| `PREDICTED_CHURN_LABEL` | NUMBER(1) | Binary prediction (0 = retained, 1 = churned) |
| `RISK_SCORE` | NUMBER(3) | Risk score (0-100) for display |
| `MODEL_VERSION` | VARCHAR2(50) | Version of model used for prediction |
| `CREATED_AT` | TIMESTAMP | When record was created |

## Indexes

```sql
CREATE INDEX idx_churn_history_user_date 
ON OML.CHURN_PREDICTIONS_HISTORY(USER_ID, SNAPSHOT_DATE DESC);

CREATE INDEX idx_churn_history_date 
ON OML.CHURN_PREDICTIONS_HISTORY(SNAPSHOT_DATE DESC);
```

## Relationship to Other Tables

```
CHURN_PREDICTIONS (Current)
    ↓ (Weekly snapshot)
CHURN_PREDICTIONS_HISTORY (Historical)
```

- **CHURN_PREDICTIONS**: Current predictions (latest)
- **CHURN_PREDICTIONS_HISTORY**: Historical snapshots (weekly)

## Usage

### 1. Weekly Snapshot Process

```python
# After updating CHURN_PREDICTIONS, create weekly snapshot
def create_weekly_snapshot():
    current_predictions = load_from_churn_predictions()
    snapshot_date = get_last_monday()  # Weekly on Monday
    
    for prediction in current_predictions:
        insert_into_history(
            user_id=prediction.user_id,
            snapshot_date=snapshot_date,
            probability=prediction.probability,
            label=prediction.label,
            risk_score=prediction.risk_score,
            model_version=prediction.model_version
        )
```

### 2. Trend Calculations

```sql
-- Calculate "↑ 12 from last week"
WITH current_week AS (
    SELECT COUNT(*) AS at_risk_count
    FROM OML.CHURN_PREDICTIONS
    WHERE PREDICTED_CHURN_LABEL = 1
),
last_week AS (
    SELECT COUNT(*) AS at_risk_count
    FROM OML.CHURN_PREDICTIONS_HISTORY
    WHERE SNAPSHOT_DATE = (
        SELECT MAX(SNAPSHOT_DATE) 
        FROM OML.CHURN_PREDICTIONS_HISTORY
    )
    AND PREDICTED_CHURN_LABEL = 1
)
SELECT 
    current_week.at_risk_count - last_week.at_risk_count AS trend_change
FROM current_week, last_week;
```

### 3. 7-Week Chart Data

```sql
-- Get last 7 weeks of at-risk customer counts
SELECT 
    SNAPSHOT_DATE,
    COUNT(*) AS at_risk_count,
    AVG(PREDICTED_CHURN_PROBABILITY) * 100 AS avg_risk_score
FROM OML.CHURN_PREDICTIONS_HISTORY
WHERE SNAPSHOT_DATE >= ADD_MONTHS(SYSDATE, -2)  -- Last 8 weeks
  AND PREDICTED_CHURN_LABEL = 1
GROUP BY SNAPSHOT_DATE
ORDER BY SNAPSHOT_DATE DESC
FETCH FIRST 7 ROWS ONLY;
```

### 4. Average Risk Score Trend

```sql
-- Calculate "↓ 3% improved"
WITH current_week AS (
    SELECT AVG(PREDICTED_CHURN_PROBABILITY) * 100 AS avg_risk
    FROM OML.CHURN_PREDICTIONS
),
last_week AS (
    SELECT AVG(PREDICTED_CHURN_PROBABILITY) * 100 AS avg_risk
    FROM OML.CHURN_PREDICTIONS_HISTORY
    WHERE SNAPSHOT_DATE = (
        SELECT MAX(SNAPSHOT_DATE) 
        FROM OML.CHURN_PREDICTIONS_HISTORY
    )
)
SELECT 
    current_week.avg_risk - last_week.avg_risk AS trend_change
FROM current_week, last_week;
```

## Data Retention

- **Keep**: Last 12 weeks (3 months)
- **Archive**: Older data can be archived or deleted
- **Cleanup**: Run weekly after snapshot creation

```sql
-- Cleanup old history (keep last 12 weeks)
DELETE FROM OML.CHURN_PREDICTIONS_HISTORY
WHERE SNAPSHOT_DATE < ADD_MONTHS(SYSDATE, -3);
```

## Workflow

### Weekly Snapshot Process

1. **Model scores users** → Updates `CHURN_PREDICTIONS`
2. **Create snapshot** → Copy to `CHURN_PREDICTIONS_HISTORY` with `SNAPSHOT_DATE = last Monday`
3. **Cleanup old data** → Delete snapshots older than 12 weeks
4. **API queries history** → For trend calculations and charts

## Integration with API

### API Endpoint: `/api/kpi/churn/summary`

```typescript
// Calculate trend from history
const currentAtRisk = await getCurrentAtRiskCount();
const lastWeekAtRisk = await getLastWeekAtRiskCount();
const trend = currentAtRisk - lastWeekAtRisk; // "↑ 12 from last week"

// Calculate avg risk trend
const currentAvgRisk = await getCurrentAvgRisk();
const lastWeekAvgRisk = await getLastWeekAvgRisk();
const avgTrend = currentAvgRisk - lastWeekAvgRisk; // "↓ 3% improved"
```

### API Endpoint: `/api/kpi/churn/chart-data`

```typescript
// Get 7-week trend data
const history = await getLast7WeeksHistory();
// Returns: [{ date, atRiskCount, avgRiskScore }, ...]
```

## Next Steps

1. Create table `OML.CHURN_PREDICTIONS_HISTORY` (Task 1.3)
2. Implement weekly snapshot process (Task 3.9)
3. Add trend calculation to API (Task 4.x)
4. Implement cleanup job (Task 3.9)
