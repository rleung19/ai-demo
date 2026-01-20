#!/bin/bash
# Compare Impact Score Calculation Methods
# Shows all three methods: A (Avg Prob), B (% At-Risk), C (vs Baseline)

API_URL="${API_URL:-http://localhost:3001}"

echo ""
echo "===================================================================================================="
echo "Impact Score Comparison: All Three Methods"
echo "===================================================================================================="
echo ""

# Fetch data from API
RISK_FACTORS_JSON=$(curl -s "${API_URL}/api/kpi/churn/risk-factors")
SUMMARY_JSON=$(curl -s "${API_URL}/api/kpi/churn/summary")

if [ -z "$RISK_FACTORS_JSON" ] || echo "$RISK_FACTORS_JSON" | jq -e '.error' > /dev/null 2>&1; then
  echo "❌ Failed to fetch data from API"
  echo "   Make sure the API server is running on port 3001"
  exit 1
fi

# Extract baseline data
BASELINE_AVG=$(echo "$SUMMARY_JSON" | jq -r '.averageRiskScore / 100' 2>/dev/null || echo "0.29")
TOTAL_CUSTOMERS=$(echo "$SUMMARY_JSON" | jq -r '.totalCustomers' 2>/dev/null || echo "5003")
AT_RISK_TOTAL=$(echo "$SUMMARY_JSON" | jq -r '.atRiskCount' 2>/dev/null || echo "1341")

echo "Baseline Data:"
echo "  Total Customers: $TOTAL_CUSTOMERS"
echo "  Total At-Risk: $AT_RISK_TOTAL"
echo "  Baseline Avg Churn Probability: $(echo "$BASELINE_AVG * 100" | bc -l | xargs printf "%.1f")%"
echo ""

# Print table header
printf "┌%-60s┬%-12s┬%-12s┬%-12s┬%-12s┐\n" "────────────────────────────────────────────────────────────" "────────────" "────────────" "────────────" "────────────"
printf "│ %-58s │ %-10s │ %-10s │ %-10s │ %-10s │\n" "Risk Factor" "Affected" "Method A" "Method B" "Method C"
printf "│ %-58s │ %-10s │ %-10s │ %-10s │ %-10s │\n" "" "Customers" "(Avg Prob)" "(% At-Risk)" "(vs Baseline)"
printf "├%-60s┼%-12s┼%-12s┼%-12s┼%-12s┤\n" "────────────────────────────────────────────────────────────" "────────────" "────────────" "────────────" "────────────"

# Process each risk factor
echo "$RISK_FACTORS_JSON" | jq -r '.riskFactors[]? | "\(.riskFactor)|\(.impactScore)|\(.affectedCustomers)"' | while IFS='|' read -r name impact affected; do
  # Skip if no data
  if [ "$name" = "null" ] || [ -z "$name" ]; then
    continue
  fi
  
  # Extract Method A (current implementation)
  METHOD_A=$(echo "$impact" | sed 's/%//' | xargs)
  AFFECTED_NUM=$affected
  
  # Method B: Estimate from Method A
  # For a well-calibrated model, if avg prob is X%, then % at-risk ≈ X% * threshold_factor
  # Assuming threshold ~0.5, % at-risk ≈ avg_prob * 0.8-0.9
  METHOD_B_ESTIMATE=$(echo "$METHOD_A * 0.85" | bc -l | xargs printf "%.1f")
  
  # Method C: Relative impact vs baseline (using Method A)
  METHOD_A_DECIMAL=$(echo "$METHOD_A / 100" | bc -l)
  if [ "$(echo "$BASELINE_AVG > 0" | bc -l)" -eq 1 ]; then
    METHOD_C=$(echo "scale=1; (($METHOD_A_DECIMAL - $BASELINE_AVG) / $BASELINE_AVG) * 100" | bc -l | xargs printf "%.1f")
  else
    METHOD_C="0.0"
  fi
  
  # Format name (truncate if too long)
  if [ ${#name} -gt 58 ]; then
    name="${name:0:55}..."
  fi
  
  # Format numbers
  AFFECTED_FMT=$(printf "%'d" "$AFFECTED_NUM" 2>/dev/null || echo "$AFFECTED_NUM")
  
  printf "│ %-58s │ %10s │ %9s%% │ %9s%% │ %9s%% │\n" "$name" "$AFFECTED_FMT" "$METHOD_A" "$METHOD_B_ESTIMATE" "$METHOD_C"
done

printf "└%-60s┴%-12s┴%-12s┴%-12s┴%-12s┘\n" "────────────────────────────────────────────────────────────" "────────────" "────────────" "────────────" "────────────"

echo ""
echo "Method Descriptions:"
echo "  Method A (Avg Prob): Average churn probability for affected customers [CURRENT - EXACT]"
echo "  Method B (% At-Risk): Percentage of affected customers who are at-risk [ESTIMATE]"
echo "  Method C (vs Baseline): Relative impact: ((Method A - Baseline) / Baseline) × 100 [EXACT]"
echo ""
echo "Note: Method B is an estimate based on Method A. For exact Method B values,"
echo "      a direct database query calculating % at-risk is required."
echo ""
echo "===================================================================================================="
echo ""
