import { KPIDetailData } from '@/app/lib/types/kpi';

export const kpi9CLVTrajectoryData: KPIDetailData = {
  metadata: {
    id: 9,
    title: 'Customer CLV Trajectory',
    owners: ['CFO', 'CMO'],
    predictionHorizon: '90-180 Days',
    modelType: 'Neural Network with Behavioral Features',
    trainingData: '36 months customer cohort data',
    confidence: 86,
    lastUpdate: 'January 1, 2026',
    dataSources: [
      'Purchase history',
      'Channel attribution',
      'Engagement metrics',
      'Cohort analysis',
      'Retention rates',
    ],
  },
  metrics: [
    {
      label: 'Average CLV',
      value: '$342',
      trend: 'up',
      trendValue: '↑ $28 YoY',
      color: 'emerald',
    },
    {
      label: 'YoY Growth',
      value: '+$28',
      trend: 'up',
      color: 'emerald',
    },
    {
      label: 'High-Value Segment',
      value: '24%',
      trend: 'neutral',
      color: 'teal',
    },
    {
      label: 'Model Confidence',
      value: '86%',
      trend: 'neutral',
      color: 'teal',
    },
  ],
  chartData: {
    labels: ['Google Shopping', 'Organic Social', 'Email', 'Direct', 'Meta Ads', 'Influencer'],
    datasets: [
      {
        label: 'Average CLV ($)',
        data: [412, 385, 520, 445, 285, 185],
        backgroundColor: ['#10b981', '#10b981', '#10b981', '#10b981', '#f59e0b', '#f43f5e'],
        borderRadius: 6,
      },
    ],
  },
  chartOptions: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      x: { grid: { display: false } },
      y: {
        grid: { display: true },
        ticks: { callback: (v: any) => '$' + v },
      },
    },
  },
  cohorts: [
    {
      name: 'VIP Tier',
      value: '$1,240',
      label: '2,450 customers (8%)',
      riskLevel: 'low',
    },
    {
      name: 'Gold Tier',
      value: '$680',
      label: '4,820 customers (16%)',
      riskLevel: 'low',
    },
    {
      name: 'Silver Tier',
      value: '$285',
      label: '12,400 customers (41%)',
      riskLevel: 'low',
    },
    {
      name: 'Bronze Tier',
      value: '$95',
      label: '10,500 customers (35%)',
      riskLevel: 'low',
    },
  ],
  tableData: [
    {
      cohort: 'Q4 2025',
      customers: '8,420',
      avgClv: '$285',
      predicted12Month: '$385',
      growth: '+35%',
    },
    {
      cohort: 'Q3 2025',
      customers: '7,850',
      avgClv: '$342',
      predicted12Month: '$412',
      growth: '+20%',
    },
    {
      cohort: 'Q2 2025',
      customers: '6,920',
      avgClv: '$398',
      predicted12Month: '$445',
      growth: '+12%',
    },
    {
      cohort: 'Q1 2025',
      customers: '5,640',
      avgClv: '$425',
      predicted12Month: '$452',
      growth: '+6%',
    },
  ],
  insight: {
    title: '🧠 AI Model Insight',
    content:
      'CLV prediction model (neural network with behavioral features) shows Google Shopping acquires highest-LTV customers ($412 avg) while Influencer channel acquires lowest ($185 avg). Recommend reallocating 60% of influencer budget to higher-LTV channels.',
    type: 'info',
  },
  actions: [
    {
      id: '1',
      title: 'Shift Budget to High-CLV Channels',
      description:
        'Reallocate $39K/month from Influencer to Google Shopping. Expected CLV increase: $42 per new customer acquired.',
      priority: 'high',
      owner: 'CFO',
      dueDate: '14 days',
      expectedOutcome: 'Higher CLV customers',
      impact: '+$1.8M annual CLV',
    },
    {
      id: '2',
      title: 'Launch VIP Loyalty Program',
      description:
        'Target top 24% (high-value segment) with exclusive benefits: early access, free shipping, personal stylist. Increase retention from 72% to 85%.',
      priority: 'medium',
      owner: 'CMO',
      dueDate: '30 days',
      expectedOutcome: 'Better retention',
      impact: '+$180K annual value',
    },
    {
      id: '3',
      title: 'Build Lookalike Audiences from VIP Tier',
      description:
        'Create 1% lookalike audience from 2,450 VIP customers. Deploy across Meta and Google for acquisition campaigns.',
      priority: 'medium',
      owner: 'CMO',
      dueDate: '7 days',
      expectedOutcome: 'Higher quality leads',
      impact: '2.4x higher LTV expected',
    },
  ],
  impact: {
    revenueImpact: 1800000,
    costImpact: 0,
    roi: 0,
    description: 'Annual CLV Impact: $1.8M',
  },
};

