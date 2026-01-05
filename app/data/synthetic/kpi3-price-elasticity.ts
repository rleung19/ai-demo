import { KPIDetailData } from '@/app/lib/types/kpi';

export const kpi3PriceElasticityData: KPIDetailData = {
  metadata: {
    id: 3,
    title: 'Price Elasticity Forecast',
    owners: ['CFO', 'CMO'],
    predictionHorizon: '7-14 Days',
    modelType: 'Gradient Boosting with Competitor Pricing',
    trainingData: '24 months price-demand data + competitor signals',
    confidence: 91,
    lastUpdate: 'January 1, 2026',
    dataSources: [
      'Historical price points',
      'Demand curves',
      'Competitor pricing',
      'Customer price sensitivity',
      'Promotional impact',
    ],
  },
  metrics: [
    {
      label: 'Optimal Price Point',
      value: '$79',
      trend: 'neutral',
      color: 'emerald',
    },
    {
      label: 'Revenue Lift Potential',
      value: '+8.5%',
      trend: 'up',
      trendValue: 'if optimized',
      color: 'teal',
    },
    {
      label: 'Demand Increase',
      value: '+42%',
      trend: 'up',
      color: 'blue',
    },
    {
      label: 'Model Confidence',
      value: '91%',
      trend: 'neutral',
      color: 'teal',
    },
  ],
  chartData: {
    labels: ['$59', '$69', '$79', '$89', '$99', '$109', '$119'],
    datasets: [
      {
        label: 'Predicted Demand (units)',
        data: [280, 220, 180, 128, 85, 52, 30],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 3,
      },
      {
        label: 'Revenue ($K)',
        data: [16.5, 15.2, 14.2, 11.4, 8.4, 5.7, 3.6],
        borderColor: '#10b981',
        borderWidth: 2,
        tension: 0.4,
        yAxisID: 'y1',
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
        position: 'left',
        grid: { display: true },
      },
      y1: {
        position: 'right',
        grid: { display: false },
        ticks: { color: '#10b981' },
      },
    },
  },
  tableData: [
    {
      category: 'Premium Dresses',
      currentPrice: '$189',
      optimalPrice: '$169',
      elasticity: '-1.8',
      revenueImpact: '+$124K',
      recommendation: 'Reduce 10%',
    },
    {
      category: 'Everyday Basics',
      currentPrice: '$29',
      optimalPrice: '$34',
      elasticity: '-0.4',
      revenueImpact: '+$45K',
      recommendation: 'Increase 15%',
    },
    {
      category: 'Accessories',
      currentPrice: '$45',
      optimalPrice: '$45',
      elasticity: '-1.0',
      revenueImpact: '$0',
      recommendation: 'Optimal',
    },
    {
      category: 'Shoes',
      currentPrice: '$129',
      optimalPrice: '$119',
      elasticity: '-1.4',
      revenueImpact: '+$38K',
      recommendation: 'Reduce 8%',
    },
    {
      category: 'Outerwear',
      currentPrice: '$245',
      optimalPrice: '$259',
      elasticity: '-0.6',
      revenueImpact: '+$22K',
      recommendation: 'Increase 6%',
    },
  ],
  insight: {
    title: '🧠 AI Model Insight',
    content:
      'Price elasticity model (gradient boosting with competitor pricing data) shows Premium Dresses are overpriced by 10% relative to perceived value. Reducing to $169 increases demand 32% with only 10% price reduction—net positive margin. Basics category shows inelastic demand—price increase opportunity.',
    type: 'info',
  },
  actions: [
    {
      id: '1',
      title: 'A/B Test Premium Dress Pricing ($169 vs $189)',
      description:
        'Run 50/50 split test on 10% of traffic for 14 days. Track conversion rate, AOV, and margin impact. Statistical significance at n=2,400 conversions.',
      priority: 'high',
      owner: 'CMO',
      dueDate: '3 days',
      expectedOutcome: 'Validates price optimization',
      impact: '+$124K annual if validated',
    },
    {
      id: '2',
      title: 'Implement Basics Price Increase',
      description:
        'Raise Everyday Basics prices by 15% ($29→$34). Low elasticity (-0.4) indicates minimal volume impact. Consider gradual rollout.',
      priority: 'medium',
      owner: 'CFO',
      dueDate: '7 days',
      expectedOutcome: 'Margin improvement',
      impact: '+$45K margin improvement',
    },
    {
      id: '3',
      title: 'Create Value Bundles for Elastic Categories',
      description:
        'For price-sensitive categories (Dresses, Shoes), create bundle offers: "Complete the Look" sets at 15% discount vs. individual items. Maintains perceived value.',
      priority: 'medium',
      owner: 'CMO',
      dueDate: '14 days',
      expectedOutcome: 'Higher AOV',
      impact: '+18% AOV for bundles',
    },
    {
      id: '4',
      title: 'Monitor Competitor Pricing Weekly',
      description:
        'Set up automated competitor price tracking for top 50 SKUs. Alert when competitors drop prices >10% to enable rapid response.',
      priority: 'low',
      owner: 'CMO',
      dueDate: 'Ongoing',
      expectedOutcome: 'Competitive pricing',
      impact: 'Ongoing',
    },
  ],
  impact: {
    revenueImpact: 229000,
    costImpact: 0,
    roi: 0,
    description: 'Potential Revenue Lift: $229K annually',
  },
};

