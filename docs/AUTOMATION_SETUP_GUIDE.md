# Automation Setup Guide

## Quick Start: Automated Local Training

This guide shows you how to automate model training without using OML Notebooks UI.

## Option 1: Cron (Linux/Mac) ⏰

### Step 1: Make Script Executable

```bash
chmod +x scripts/train_churn_model_local.py
```

### Step 2: Test Run

```bash
python scripts/train_churn_model_local.py
```

### Step 3: Add to Crontab

```bash
crontab -e
```

Add this line to run daily at 2 AM:

```cron
0 2 * * * /path/to/python /path/to/scripts/train_churn_model_local.py >> /path/to/logs/training.log 2>&1
```

**Example** (if Python is in PATH):

```cron
0 2 * * * cd /Users/rleung/Projects/aiworkshop2026/ai-demo && python scripts/train_churn_model_local.py >> logs/training.log 2>&1
```

### Step 4: Verify

```bash
# Check cron is running
crontab -l

# Check logs
tail -f logs/training.log
```

---

## Option 2: Systemd Timer (Linux) 🔄

### Step 1: Create Service File

Create `/etc/systemd/system/churn-training.service`:

```ini
[Unit]
Description=Churn Model Training
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/path/to/ai-demo
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /path/to/ai-demo/scripts/train_churn_model_local.py
StandardOutput=append:/path/to/ai-demo/logs/training.log
StandardError=append:/path/to/ai-demo/logs/training.log
```

### Step 2: Create Timer File

Create `/etc/systemd/system/churn-training.timer`:

```ini
[Unit]
Description=Daily Churn Model Training
Requires=churn-training.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Step 3: Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable churn-training.timer
sudo systemctl start churn-training.timer
```

### Step 4: Check Status

```bash
sudo systemctl status churn-training.timer
sudo systemctl list-timers
```

---

## Option 3: Airflow DAG (Recommended for Production) 🚀

### Step 1: Create DAG File

Create `dags/churn_training_dag.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def train_churn_model():
    """Execute training script"""
    import subprocess
    script_path = project_root / 'scripts' / 'train_churn_model_local.py'
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(project_root),
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"Training failed: {result.stderr}")
    return result.stdout

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'churn_model_training',
    default_args=default_args,
    description='Daily churn model training',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['ml', 'churn'],
)

train_task = PythonOperator(
    task_id='train_churn_model',
    python_callable=train_churn_model,
    dag=dag,
)

train_task
```

### Step 2: Deploy to Airflow

```bash
# Copy DAG to Airflow DAGs folder
cp dags/churn_training_dag.py $AIRFLOW_HOME/dags/
```

### Step 3: Verify in Airflow UI

1. Open Airflow UI
2. Find `churn_model_training` DAG
3. Enable it
4. Monitor runs

---

## Option 4: GitHub Actions (CI/CD) 🔧

### Step 1: Create Workflow

Create `.github/workflows/train-model.yml`:

```yaml
name: Train Churn Model

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Train model
        env:
          ADB_USERNAME: ${{ secrets.ADB_USERNAME }}
          ADB_PASSWORD: ${{ secrets.ADB_PASSWORD }}
          ADB_CONNECTION_STRING: ${{ secrets.ADB_CONNECTION_STRING }}
          ADB_WALLET_PATH: ${{ secrets.ADB_WALLET_PATH }}
        run: |
          python scripts/train_churn_model_local.py
      
      - name: Upload logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: training-logs
          path: logs/
```

### Step 2: Add Secrets

In GitHub repository:
1. Go to Settings → Secrets → Actions
2. Add:
   - `ADB_USERNAME`
   - `ADB_PASSWORD`
   - `ADB_CONNECTION_STRING`
   - `ADB_WALLET_PATH`

---

## Option 5: Oracle Scheduler (If OML4Py Available) 🗄️

### Step 1: Create PL/SQL Procedure

```sql
CREATE OR REPLACE PROCEDURE OML.TRAIN_CHURN_MODEL AS
BEGIN
    -- This would call Python script via EXTPROC
    -- Requires EXTPROC setup and Python script accessible to database
    DBMS_SCHEDULER.CREATE_JOB(
        job_name => 'TRAIN_CHURN_MODEL_JOB',
        job_type => 'EXECUTABLE',
        job_action => '/path/to/python /path/to/scripts/train_churn_model_local.py',
        start_date => SYSTIMESTAMP,
        repeat_interval => 'FREQ=DAILY;BYHOUR=2;BYMINUTE=0',
        enabled => TRUE
    );
END;
/
```

**Note**: This requires EXTPROC configuration and may not work in all ADB environments.

---

## Monitoring & Alerts

### Email Alerts on Failure

Add to your script or cron:

```bash
# In cron:
0 2 * * * /path/to/python /path/to/scripts/train_churn_model_local.py >> /path/to/logs/training.log 2>&1 || echo "Training failed" | mail -s "Churn Model Training Failed" your-email@example.com
```

### Slack Alerts

Add to `train_churn_model_local.py`:

```python
import requests

def send_slack_alert(message, webhook_url):
    """Send alert to Slack"""
    payload = {'text': message}
    requests.post(webhook_url, json=payload)

# In main():
if return_code != 0:
    send_slack_alert("❌ Churn model training failed", SLACK_WEBHOOK_URL)
```

---

## Best Practices

1. **Logging**: All runs are logged to `logs/` directory
2. **Error Handling**: Script exits with non-zero code on failure
3. **Model Versioning**: Each run creates a new model version
4. **Database Storage**: Model metadata stored in `OML.MODEL_METADATA` table
5. **Backup**: Model files saved to `models/` directory (optional)

---

## Troubleshooting

### Script Fails to Connect

- Check `.env` file has correct credentials
- Verify ADB is accessible
- Test connection manually: `python scripts/test-python-connection.py`

### Model Performance Low

- Check data quality: `python scripts/validate_churn_data.py`
- Review feature engineering views
- Check training data size

### Cron Not Running

- Check cron service: `sudo service cron status`
- Check cron logs: `grep CRON /var/log/syslog`
- Verify PATH in cron: Use full paths in cron commands

---

## Summary

| Method | Complexity | Best For |
|--------|-----------|----------|
| **Cron** | Low | Simple scheduling |
| **Systemd** | Medium | Linux servers |
| **Airflow** | High | Production pipelines |
| **GitHub Actions** | Medium | CI/CD integration |
| **Oracle Scheduler** | High | Database integration |

**Recommended**: Start with **Cron** for simplicity, move to **Airflow** for production.
