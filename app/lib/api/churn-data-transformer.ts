/**
 * Transform API data to KPI data format
 * Converts churn API responses to KPIDetailData format
 */

import { KPIDetailData } from '@/app/lib/types/kpi';
import {
  ChurnSummary,
  ChurnCohort,
  ChurnMetrics,
  ChartData,
  RiskFactor,
} from './churn-api';
import { kpi1ChurnRiskData } from '@/app/data/synthetic/kpi1-churn-risk';

/**
 * Format number with commas
 */
function formatNumber(num: number): string {
  return num.toLocaleString();
}

/**
 * Format currency
 */
function formatCurrency(num: number): string {
  if (num >= 1000000) {
    return `$${(num / 1000000).toFixed(1)}M`;
  } else if (num >= 1000) {
    return `$${(num / 1000).toFixed(0)}K`;
  }
  return `$${num.toFixed(0)}`;
}

/**
 * Format percentage
 */
function formatPercentage(num: number, decimals = 1): string {
  return `${num.toFixed(decimals)}%`;
}

/**
 * Format date
 */
function formatDate(dateString: string | null): string {
  if (!dateString) return 'Unknown';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return 'Unknown';
  }
}

/**
 * Build dynamic business impact from summary data.
 * Calculates revenue impact from totalLTVAtRisk, estimates cost impact, and calculates ROI.
 * 
 * Note: LTV (Lifetime Value) is estimated as 2x the total spent in the last 24 months,
 * representing projected future value. For Revenue Impact, we use a conservative recovery
 * estimate (30-40% of LTV) since not all churn can be prevented.
 */
function buildImpactFromData(
  summary: ChurnSummary | null
): KPIDetailData['impact'] | null {
  if (!summary || summary.totalLTVAtRisk === undefined || summary.totalLTVAtRisk === null) {
    return null;
  }

  // LTV is projected future value (2x 24-month spending)
  // For Revenue Impact, use a conservative recovery estimate: 35% of LTV at risk
  // This represents recoverable revenue if retention campaigns are successful
  // (Not all churn can be prevented, and not all LTV is immediately recoverable)
  const RECOVERY_RATE = 0.35;
  const revenueImpact = summary.totalLTVAtRisk * RECOVERY_RATE;

  // Cost impact: Estimate as ~7.5% of recoverable revenue (typical for retention campaigns)
  // This represents the cost of interventions (discounts, outreach, etc.)
  const costImpact = revenueImpact * 0.075;

  // ROI calculation: (Revenue Impact - Cost Impact) / Cost Impact * 100
  const roi = costImpact > 0 ? ((revenueImpact - costImpact) / costImpact) * 100 : 0;

  return {
    revenueImpact,
    costImpact,
    roi: Math.round(roi),
    description: `Net ROI: ${Math.round(roi)}% (Recovery - Cost) / Cost. Based on 35% recovery rate of LTV at risk.`,
  };
}

/**
 * Build dynamic recommended actions from risk factors and cohort data.
 * Replaces static numbers with actual data from the API.
 */
function buildActionsFromData(
  riskFactors: RiskFactor[] | null,
  cohorts: ChurnCohort[] | null,
  summary: ChurnSummary | null
): KPIDetailData['actions'] {
  const baseActions = kpi1ChurnRiskData.actions;
  
  if (!riskFactors || riskFactors.length === 0) {
    return baseActions;
  }

  // Find specific risk factors (match definition-style names)
  const returnsRate = riskFactors.find((rf) =>
    rf.riskFactor.toLowerCase().includes('returns') || rf.riskFactor.toLowerCase().includes('size') || rf.riskFactor.toLowerCase().includes('fit')
  );
  const emailDecay = riskFactors.find((rf) =>
    rf.riskFactor.toLowerCase().includes('email') || rf.riskFactor.toLowerCase().includes('open rate')
  );
  const noPurchase = riskFactors.find((rf) =>
    rf.riskFactor.toLowerCase().includes('purchase') || rf.riskFactor.toLowerCase().includes('dormant')
  );

  // Find cohort data
  const vipCohort = cohorts?.find((c) => c.cohort === 'VIP');
  const dormantCohort = cohorts?.find((c) => c.cohort === 'Dormant');

  // Transform actions with real data
  return baseActions.map((action) => {
    // Action #2: Address Returns rate > 20%
    if (action.id === '2' && returnsRate) {
      return {
        ...action,
        title: `Address Returns rate > 20% for ${formatNumber(returnsRate.affectedCustomers)} Customers`,
        description: `Proactive outreach to ${formatNumber(returnsRate.affectedCustomers)} customers with returns rate > 20%. Offer free exchange, size guide consultation, and $20 credit for next purchase.`,
      };
    }

    // Action #3: Win-back Email Sequence for Dormant Segment
    if (action.id === '3') {
      // Prioritize actual dormant cohort data - use customerCount (total dormant) for win-back campaign
      // Only fall back to risk factor or static data if cohort is not available
      const dormantCount = dormantCohort?.customerCount || dormantCohort?.atRiskCount || noPurchase?.affectedCustomers || 97;
      return {
        ...action,
        title: `Win-back Email Sequence for ${formatNumber(dormantCount)} Dormant Customers`,
        description: `Deploy 4-email sequence for ${formatNumber(dormantCount)} dormant customers: "We miss you" → Product recommendations → Exclusive offer → Final reminder with urgency.`,
      };
    }

    // Action #1: Launch VIP Re-engagement Campaign
    if (action.id === '1' && vipCohort) {
      const vipAtRiskCount = vipCohort.atRiskCount || 150;
      return {
        ...action,
        title: `Launch VIP Re-engagement Campaign`,
        description: `Target ${formatNumber(vipAtRiskCount)} VIP customers with personalized 20% discount on AI selected products that each customer will likely to buy. Include dedicated stylist consultation offer.`,
      };
    }

    // Action #4: High-Touch Outreach for Top VIPs
    if (action.id === '4' && vipCohort) {
      const topVipCount = Math.min(50, vipCohort.atRiskCount || 50);
      return {
        ...action,
        title: `High-Touch Outreach for Top ${formatNumber(topVipCount)} VIPs`,
        description: `Personal phone calls from customer success team to ${formatNumber(topVipCount)} highest-value at-risk customers. Collect feedback and offer exclusive preview access.`,
      };
    }

    return action;
  });
}

/**
 * Build dynamic AI model insight from risk factors (if available).
 * Falls back to static insight when no usable risk factors are present.
 */
function buildInsightFromRiskFactors(
  riskFactors: RiskFactor[] | null
): KPIDetailData['insight'] | null {
  if (!riskFactors || riskFactors.length === 0) {
    return null;
  }

  // Parse impact scores and keep only factors with a valid numeric score
  const factorsWithScore = riskFactors
    .map((rf) => {
      const numericScore = parseFloat(String(rf.impactScore).replace('%', '').trim());
      return {
        ...rf,
        numericScore: Number.isFinite(numericScore) ? numericScore : 0,
      };
    })
    .filter((rf) => rf.numericScore > 0);

  if (factorsWithScore.length === 0) {
    return null;
  }

  // Sort by impact descending and take the top few factors
  factorsWithScore.sort((a, b) => b.numericScore - a.numericScore);
  const topFactors = factorsWithScore.slice(0, 3);
  const primary = topFactors[0];

  const factorNames = topFactors.map((f) => f.riskFactor).join(' + ');

  // Collect unique primary segments from the top factors
  const affectedSegments = Array.from(
    new Set(
      topFactors
        .map((f) => f.primarySegment)
        .join(', ')
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean)
    )
  );

  const segmentsText =
    affectedSegments.length > 0
      ? ` These signals primarily affect ${affectedSegments.join(', ')} segments.`
      : '';

  return {
    title: '🧠 AI Model Insight',
    content: `The churn prediction model currently ranks ${factorNames} as the strongest predictors of churn, with top impact scores up to ${primary.numericScore.toFixed(
      0
    )}%.${segmentsText}`,
    type: 'info',
  };
}

/**
 * Transform API data to KPI #1 data format
 */
export function transformChurnDataToKPI(
  summary: ChurnSummary | null,
  cohorts: ChurnCohort[] | null,
  metrics: ChurnMetrics | null,
  chartData: ChartData | null,
  riskFactors: RiskFactor[] | null = null,
  useFallback = false
): KPIDetailData {
  // Use fallback data if API data is not available
  if (!summary || !cohorts || !metrics) {
    return {
      ...kpi1ChurnRiskData,
      metadata: {
        ...kpi1ChurnRiskData.metadata,
        ...(useFallback && {
          note: 'Using cached data',
        }),
      },
    };
  }

  // Find VIP cohort for alert
  const vipCohort = cohorts.find((c) => c.cohort === 'VIP');
  const atRiskCohort = cohorts.find((c) => c.cohort === 'At-Risk');

  // Build alert message
  const alertTitle = `${formatNumber(summary.atRiskCount)} High-Value Customers at Risk`;
  const alertDescription = `AI model predicts ${formatCurrency(
    summary.totalLTVAtRisk
  )} in LTV at risk within 60-90 days. ${
    vipCohort
      ? `VIP segment shows ${formatPercentage(
          vipCohort.averageRiskScore
        )} churn probability.`
      : ''
  }`;

  // Transform metrics
  const transformedMetrics = [
    {
      label: 'At-Risk Customers',
      value: formatNumber(summary.atRiskCount),
      trend: 'neutral' as const,
      color: 'rose' as const,
    },
    {
      label: 'Avg Risk Score',
      value: formatPercentage(summary.averageRiskScore),
      trend: 'neutral' as const,
      color: 'amber' as const,
    },
    {
      label: 'LTV at Risk',
      value: formatCurrency(summary.totalLTVAtRisk),
      trend: 'neutral' as const,
      color: 'rose' as const,
    },
    {
      label: 'Model Confidence',
      value: metrics.modelConfidence
        ? formatPercentage(metrics.modelConfidence * 100, 1)
        : 'N/A',
      trend: 'neutral' as const,
      color: 'teal' as const,
    },
  ];

  // Transform cohorts
  const transformedCohorts = cohorts.map((cohort) => {
    let riskLevel: 'low' | 'medium' | 'high' = 'low';
    if (cohort.averageRiskScore >= 50) riskLevel = 'high';
    else if (cohort.averageRiskScore >= 30) riskLevel = 'medium';

    // Build at-risk label with churn probability if available
    let atRiskLabel = formatNumber(cohort.atRiskCount);
    if (
      cohort.atRiskCount > 0 &&
      typeof cohort.averageRiskScoreAtRisk === 'number' &&
      !isNaN(cohort.averageRiskScoreAtRisk)
    ) {
      atRiskLabel = `${atRiskLabel} at-risk (${formatPercentage(cohort.averageRiskScoreAtRisk, 1)} Chance)`;
    } else {
      atRiskLabel = `${atRiskLabel} at-risk`;
    }

    return {
      name: `${cohort.cohort} Customers`,
      value: formatPercentage(cohort.averageRiskScore),
      label: `${formatNumber(cohort.customerCount)} total\n${atRiskLabel}\n${formatCurrency(
        cohort.ltvAtRisk
      )} LTV at Risk`,
      riskLevel,
    };
  });

  // Transform chart data
  let transformedChartData = kpi1ChurnRiskData.chartData;
  if (chartData && chartData.data.length > 0) {
    // Use cohort data for chart if available
    if (cohorts.length > 0) {
      transformedChartData = {
        labels: cohorts.map((c) => c.cohort),
        datasets: [
          {
            label: 'Churn Probability %',
            data: cohorts.map((c) => c.averageRiskScore),
            backgroundColor: cohorts.map((c) => {
              if (c.averageRiskScore >= 50) return '#f43f5e';
              if (c.averageRiskScore >= 30) return '#f59e0b';
              return '#10b981';
            }),
            borderRadius: 6,
            yAxisID: 'y',
          },
          {
            label: 'At-Risk Count',
            data: cohorts.map((c) => c.atRiskCount),
            backgroundColor: 'rgba(244, 63, 94, 0.3)',
            borderColor: '#f43f5e',
            borderWidth: 2,
            borderRadius: 6,
            yAxisID: 'y1',
          },
        ],
      };
    }
  }

  // Prefer dynamic insight based on risk factors when available; otherwise fall back to static copy
  const dynamicInsight = buildInsightFromRiskFactors(riskFactors);

  return {
    metadata: {
      id: 1,
      title: 'Churn Risk Score (Cohort)',
      owners: ['CMO', 'COO'],
      predictionHorizon: '60-90 Days',
      modelType: metrics.modelType || 'XGBoost Binary Classification',
      trainingData: `${formatNumber(
        metrics.trainingStats.trainSamples
      )} training samples`,
      confidence: metrics.modelConfidence
        ? Math.round(metrics.modelConfidence * 100)
        : 82,
      lastUpdate: formatDate(metrics.lastUpdate),
      dataSources: [
        'Login frequency',
        'Support tickets',
        'NPS sentiment',
        'Purchase velocity',
        'Email engagement',
        'Browse-to-cart ratio',
      ],
      ...(useFallback && {
        note: 'Using cached data - API unavailable',
      }),
    },
    alert: {
      icon: '⚠️',
      title: alertTitle,
      description: alertDescription,
    },
    metrics: transformedMetrics,
    chartData: transformedChartData,
    chartOptions: {
      ...kpi1ChurnRiskData.chartOptions,
      plugins: {
        ...(kpi1ChurnRiskData.chartOptions?.plugins || {}),
        tooltip: {
          ...(kpi1ChurnRiskData.chartOptions?.plugins?.tooltip || {}),
          callbacks: {
            ...(kpi1ChurnRiskData.chartOptions?.plugins?.tooltip?.callbacks || {}),
            label: function (context: any) {
              const datasetLabel = context.dataset.label || '';
              const value = context.parsed.y ?? context.parsed;
              const baseLabel = datasetLabel ? `${datasetLabel}: ${value.toFixed(1)}%` : `${value.toFixed(1)}%`;

              const index = context.dataIndex;
              const cohort = cohorts[index];
              if (
                cohort &&
                typeof cohort.averageRiskScoreAtRisk === 'number' &&
                cohort.atRiskCount > 0
              ) {
                const atRiskLabel = formatPercentage(cohort.averageRiskScoreAtRisk, 1);
                return `${baseLabel} (Avg at-risk churn: ${atRiskLabel})`;
              }

              return baseLabel;
            },
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
        },
        y: {
          type: 'linear' as const,
          position: 'left' as const,
          title: {
            display: true,
            text: 'Churn Probability %',
          },
          min: 0,
          max: 100,
          ticks: {
            callback: (value: any) => value + '%',
          },
          grid: { display: true },
        },
        y1: {
          type: 'linear' as const,
          position: 'right' as const,
          title: {
            display: true,
            text: 'At-Risk Count',
          },
          min: 0,
          ticks: {
            callback: (value: any) => Math.round(value).toLocaleString(),
          },
          grid: { display: false },
        },
      },
    },
    cohorts: transformedCohorts,
    tableData: riskFactors && riskFactors.length > 0
      ? riskFactors.map((rf) => ({
          riskFactor: rf.riskFactor,
          impactScore: rf.impactScore,
          affectedCustomers: rf.affectedCustomers,
          primarySegment: rf.primarySegment,
        }))
      : kpi1ChurnRiskData.tableData, // Use API data if available, otherwise fallback to static
    actions: buildActionsFromData(riskFactors, cohorts, summary),
    impact: buildImpactFromData(summary) ?? kpi1ChurnRiskData.impact,
    insight: dynamicInsight ?? kpi1ChurnRiskData.insight,
  };
}
