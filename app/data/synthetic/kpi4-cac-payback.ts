import { KPIDetailData } from '@/app/lib/types/kpi';

export const kpi4CACPaybackData: KPIDetailData = {
  metadata: {
    id: 4,
    title: 'CAC Payback Period Trend',
    owners: ['CFO', 'CMO'],
    predictionHorizon: '30-60 Days',
    modelType: 'Time-Series Forecasting',
    trainingData: '24 months channel performance data',
    confidence: 88,
    lastUpdate: 'January 1, 2026',
    dataSources: [
      'Channel CAC',
      'Customer LTV',
      'Payback periods',
      'Channel mix',
      'Attribution data',
    ],
  },
  metrics: [
    {
      label: 'Months to Payback',
      value: '8.2',
      trend: 'down',
      trendValue: '↓ 1.3 improving',
      color: 'emerald',
    },
    {
      label: 'Month Improvement',
      value: '↓1.3',
      trend: 'down',
      color: 'emerald',
    },
    {
      label: 'Blended CAC',
      value: '$48',
      trend: 'neutral',
      color: 'blue',
    },
    {
      label: 'Model Confidence',
      value: '88%',
      trend: 'neutral',
      color: 'teal',
    },
  ],
  chartData: {
    labels: ['Email', 'Organic Social', 'Google Shopping', 'Meta Ads', 'Influencer'],
    datasets: [
      {
        label: 'Payback Period (months)',
        data: [0.8, 2.1, 4.8, 8.2, 14.2],
        backgroundColor: ['#10b981', '#10b981', '#10b981', '#f59e0b', '#f43f5e'],
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
        max: 18,
        ticks: { callback: (v: any) => v + ' mo' },
      },
    },
  },
  tableData: [
    {
      channel: 'Google Shopping',
      cac: '$32',
      ltvCac: '5.2:1',
      payback: '4.8 mo',
      monthlySpend: '$85K',
      recommendation: 'Scale +40%',
    },
    {
      channel: 'Organic Social',
      cac: '$18',
      ltvCac: '8.4:1',
      payback: '2.1 mo',
      monthlySpend: '$25K',
      recommendation: 'Scale +60%',
    },
    {
      channel: 'Meta Ads',
      cac: '$52',
      ltvCac: '3.1:1',
      payback: '8.2 mo',
      monthlySpend: '$120K',
      recommendation: 'Optimize',
    },
    {
      channel: 'Influencer',
      cac: '$78',
      ltvCac: '1.8:1',
      payback: '14.2 mo',
      monthlySpend: '$65K',
      recommendation: 'Reduce 60%',
    },
    {
      channel: 'Email',
      cac: '$8',
      ltvCac: '18.5:1',
      payback: '0.8 mo',
      monthlySpend: '$12K',
      recommendation: 'Invest more',
    },
  ],
  insight: {
    title: '🧠 AI Model Insight',
    content:
      'CAC payback model identifies Influencer channel is underperforming with 14.2-month payback (target: <12 months). Customers acquired via influencers have 35% lower repeat purchase rate. Recommend shifting 60% of influencer budget to Google Shopping and Organic Social.',
    type: 'warning',
  },
  actions: [
    {
      id: '1',
      title: 'Pause Low-ROI Influencer Partnerships',
      description:
        'Reduce influencer spend by $39K/month (60% reduction). Maintain only top 3 micro-influencers with proven >3:1 LTV:CAC ratio.',
      priority: 'high',
      owner: 'CMO',
      dueDate: '7 days',
      expectedOutcome: 'Cost savings',
      impact: 'Saves $468K annually',
    },
    {
      id: '2',
      title: 'Scale Google Shopping Budget +40%',
      description:
        'Increase Google Shopping spend from $85K to $119K monthly. 5.2:1 LTV:CAC ratio supports expansion. Focus on product-level ROAS optimization.',
      priority: 'medium',
      owner: 'CMO',
      dueDate: '30 days',
      expectedOutcome: 'Revenue growth',
      impact: '+$180K revenue/month',
    },
    {
      id: '3',
      title: 'Implement Lookalike Audiences on Best Cohorts',
      description:
        'Build 1% lookalike audiences from customers with <6 month payback. Deploy across Meta and Google for new customer acquisition.',
      priority: 'medium',
      owner: 'CMO',
      dueDate: '14 days',
      expectedOutcome: 'Lower CAC',
      impact: 'Expected 25% CAC reduction',
    },
  ],
  impact: {
    revenueImpact: 2160000,
    costImpact: 468000,
    roi: 362,
    description: 'Annual Savings: $468K, Revenue Growth: $2.16M',
  },
};

