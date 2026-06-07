#!/usr/bin/env python3
"""Hit Express churn API and compare key metrics to ADB baseline."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASELINE = Path(__file__).resolve().parent / "fixtures" / "adb_baseline.json"
API_BASE = "http://localhost:3001"


def get(path: str) -> dict:
    req = urllib.request.Request(f"{API_BASE}{path}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def main() -> None:
    baseline = json.loads(BASELINE.read_text())
    failures = []

    health = get("/api/health")
    if health.get("database", {}).get("backend") != "postgres":
        failures.append(f"expected postgres backend, got {health.get('database')}")
    if not health.get("database", {}).get("connected"):
        failures.append("health: database not connected")

    summary = get("/api/kpi/churn/summary")
    exp = baseline["summary"]
    checks = [
        ("totalCustomers", int(summary["totalCustomers"]), int(exp["total_customers"])),
        ("atRiskCount", int(summary["atRiskCount"]), int(exp["at_risk_count"])),
        ("totalLTVAtRisk", round(float(summary["totalLTVAtRisk"]), 2), round(float(exp["total_ltv_at_risk"]), 2)),
    ]
    for name, got, want in checks:
        if got != want:
            failures.append(f"summary.{name}: {got} != {want}")

    cohorts = {c["cohort"]: c for c in get("/api/kpi/churn/cohorts")["cohorts"]}
    for row in baseline["cohorts"]:
        name = row["cohort"]
        if name not in cohorts:
            failures.append(f"cohort missing: {name}")
            continue
        if int(cohorts[name]["customerCount"]) != int(row["customer_count"]):
            failures.append(
                f"cohort.{name}.customerCount: {cohorts[name]['customerCount']} != {row['customer_count']}"
            )

    risk = get("/api/kpi/churn/risk-factors")
    if len(risk.get("riskFactors", [])) < 1:
        failures.append("riskFactors empty")

    if failures:
        print("❌ API parity failures:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print("✓ API parity checks passed (postgres backend)")
    print(f"  summary: {summary['totalCustomers']} customers, {summary['atRiskCount']} at-risk")
    print(f"  cohorts: {len(cohorts)}, risk factors: {len(risk['riskFactors'])}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:
        print(f"❌ Cannot reach API at {API_BASE}: {exc}")
        print("   Start server: npm run server:dev:postgres")
        sys.exit(1)
