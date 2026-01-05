import { KPIDetailData } from '@/app/lib/types/kpi';

export const kpi6EmailDecayData: KPIDetailData = {
  metadata: {
    id: 6,
    title: 'Email Engagement Decay',
    owners: ['CMO'],
    predictionHorizon: '14-30 Days',
    modelType: 'Time-Series Decay Model',
    trainingData: '24 months email engagement data',
    confidence: 79,
    lastUpdate: 'January 1, 2026',
    dataSources: [
      'Open rates',
      'Click rates',
      'Unsubscribe rates',
      'Campaign frequency',
      'Content performance',
    ],
  },
  alert: {
    icon: '📧',
    title: 'Email Engagement Declining 0.8% Weekly',
    description:
      'Open rates dropping from 38% to 36% over past 4 weeks. 2,400 subscribers predicted to churn within 30 days. List value at risk: $50K.',
  },
  metrics: [
    {
      label: 'Weekly Decay Rate',
      value: '-0.8%',
      trend: 'down',
      trendValue: 'per week',
      color: 'amber',
    },
    {
      label: 'At-Risk Subscribers',
      value: '2.4K',
      trend: 'neutral',
      color: 'rose',
    },
    {
      label: 'Current Open Rate',
      value: '36%',
      trend: 'down',
      color: 'amber',
    },
    {
      label: 'Model Confidence',
      value: '79%',
      trend: 'neutral',
      color: 'amber',
    },
  ],
  chartData: {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
    datasets: [
      {
        label: 'Open Rate %',
        data: [42, 41, 40, 39, 38, 37.5, 36.5, 36],
        borderColor: '#f97316',
        backgroundColor: 'rgba(249, 115, 22, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 3,
      },
      {
        label: 'Target (40%)',
        data: [40, 40, 40, 40, 40, 40, 40, 40],
        borderColor: '#10b981',
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0,
      },
    ],
  },
  chartOptions: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' },
    },
    scales: {
      x: { grid: { display: false } },
      y: {
        grid: { display: true },
        min: 30,
        max: 50,
        ticks: { callback: (v: any) => v + '%' },
      },
    },
  },
  tableData: [
    {
      campaignType: 'VIP Exclusive',
      openRate: '52%',
      ctr: '8.4%',
      revenue: '$28K',
      optimalSendTime: '10:00 AM',
    },
    {
      campaignType: 'Flash Sale',
      openRate: '48%',
      ctr: '12.2%',
      revenue: '$45K',
      optimalSendTime: '7:00 PM',
    },
    {
      campaignType: 'Abandoned Cart',
      openRate: '38%',
      ctr: '6.8%',
      revenue: '$32K',
      optimalSendTime: '2 hrs after',
    },
    {
      campaignType: 'New Arrivals',
      openRate: '32%',
      ctr: '4.2%',
      revenue: '$18K',
      optimalSendTime: '11:00 AM',
    },
    {
      campaignType: 'Weekly Newsletter',
      openRate: '24%',
      ctr: '2.1%',
      revenue: '$8K',
      optimalSendTime: 'Saturday 9AM',
    },
  ],
  insight: {
    title: '🧠 AI Model Insight',
    content:
      'Engagement decay model identifies over-mailing (5+ emails/week) as primary driver. Subscribers receiving 3 emails/week show 45% higher engagement. Weekly newsletter has lowest ROI—consider reducing frequency or sunsetting.',
    type: 'warning',
  },
  actions: [
    {
      id: '1',
      title: 'Launch Re-engagement Flow for 2,400 At-Risk Subs',
      description:
        'Deploy 4-email sequence: "We miss you" → Curated picks → Exclusive 20% off → Last chance. Reduce cadence to 1 email/week for this segment.',
      priority: 'high',
      owner: 'CMO',
      dueDate: '7 days',
      expectedOutcome: 'Reactivation',
      impact: '12-18% reactivation rate',
    },
    {
      id: '2',
      title: 'Clean Inactive Subscribers (90+ Days)',
      description:
        'Move 1,200 subscribers with 0 opens in 90 days to suppression list. Improves deliverability score and reduces ESP costs.',
      priority: 'medium',
      owner: 'CMO',
      dueDate: '3 days',
      expectedOutcome: 'Better deliverability',
      impact: '+8% deliverability',
    },
    {
      id: '3',
      title: 'A/B Test Subject Lines with Personalization',
      description:
        'Test personalized subject lines (first name, recent browse category) vs. generic. Target 15% open rate improvement.',
      priority: 'medium',
      owner: 'CMO',
      dueDate: 'Ongoing',
      expectedOutcome: 'Higher engagement',
      impact: '+$12K monthly revenue',
    },
  ],
  impact: {
    revenueImpact: 144000,
    costImpact: 0,
    roi: 0,
    description: 'Annual Revenue Impact: $144K',
  },
};

