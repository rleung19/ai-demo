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
 * Transform API data to KPI #1 data format
 */
export function transformChurnDataToKPI(
  summary: ChurnSummary | null,
  cohorts: ChurnCohort[] | null,
  metrics: ChurnMetrics | null,
  chartData: ChartData | null,
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

    return {
      name: `${cohort.cohort} Customers`,
      value: formatPercentage(cohort.averageRiskScore),
      label: `${formatNumber(cohort.customerCount)} total • ${formatNumber(cohort.atRiskCount)} at-risk • ${formatCurrency(
        cohort.ltvAtRisk
      )} LTV`,
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
    tableData: kpi1ChurnRiskData.tableData, // Include risk factors table data
    actions: kpi1ChurnRiskData.actions,
    impact: kpi1ChurnRiskData.impact,
    insight: kpi1ChurnRiskData.insight,
  };
}
