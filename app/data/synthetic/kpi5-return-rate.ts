import { KPIDetailData } from '@/app/lib/types/kpi';

export const kpi5ReturnRateData: KPIDetailData = {
  metadata: {
    id: 5,
    title: 'Return Rate Predictor',
    owners: ['COO', 'CMO'],
    predictionHorizon: '10-21 Days',
    modelType: 'Random Forest with NLP Review Analysis',
    trainingData: '24 months return data + review sentiment',
    confidence: 85,
    lastUpdate: 'January 1, 2026',
    dataSources: [
      'Return history',
      'Product reviews',
      'Size chart accuracy',
      'Product photography',
      'Customer feedback',
    ],
  },
  alert: {
    icon: '📦',
    title: 'Return Rate Predicted to Reach 28%',
    description:
      'AI model predicts 28% return rate in next 21 days vs. 22% target. 12 SKUs flagged with >35% predicted return rate—primarily due to size/fit issues in Shoes and Dresses categories.',
  },
  metrics: [
    {
      label: 'Predicted Rate',
      value: '28%',
      trend: 'up',
      trendValue: 'vs. 22% target',
      color: 'amber',
    },
    {
      label: 'Flagged Items',
      value: 12,
      trend: 'neutral',
      color: 'rose',
    },
    {
      label: 'Logistics Cost Impact',
      value: '$42K',
      trend: 'neutral',
      color: 'rose',
    },
    {
      label: 'Model Confidence',
      value: '85%',
      trend: 'neutral',
      color: 'teal',
    },
  ],
  chartData: {
    labels: ['Shoes', 'Dresses', 'Outerwear', 'Bottoms', 'Tops', 'Accessories'],
    datasets: [
      {
        label: 'Current Rate %',
        data: [32, 28, 26, 24, 18, 12],
        backgroundColor: 'rgba(148, 163, 184, 0.6)',
        borderRadius: 6,
      },
      {
        label: 'Predicted Rate %',
        data: [38, 32, 30, 28, 20, 14],
        backgroundColor: '#f43f5e',
        borderRadius: 6,
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
        ticks: { callback: (v: any) => v + '%' },
      },
    },
  },
  tableData: [
    {
      product: 'Strappy Sandal Gold 36-40',
      category: 'Shoes',
      predictedRate: '48%',
      primaryReason: 'Runs small',
      costImpact: '$8,200',
    },
    {
      product: 'Fitted Blazer Navy XS-M',
      category: 'Outerwear',
      predictedRate: '42%',
      primaryReason: 'Runs small',
      costImpact: '$6,800',
    },
    {
      product: 'Wrap Dress Floral S-L',
      category: 'Dresses',
      predictedRate: '38%',
      primaryReason: 'Color differs',
      costImpact: '$5,400',
    },
    {
      product: 'Skinny Jean Black 24-30',
      category: 'Bottoms',
      predictedRate: '35%',
      primaryReason: 'Sizing inconsistent',
      costImpact: '$4,200',
    },
  ],
  insight: {
    title: '🧠 AI Model Insight',
    content:
      'Return prediction model (random forest with NLP review analysis) identifies sizing inconsistency as #1 driver (62% of returns). Customers mentioning "runs small" in first review predict 3.2x higher return rate. Recommend immediate size chart updates for flagged SKUs.',
    type: 'warning',
  },
  actions: [
    {
      id: '1',
      title: 'Update Size Charts for 12 Flagged Items',
      description:
        'Add "runs small—size up" guidance prominently on PDPs. Include detailed measurements in cm/inches. Add customer review sizing insights.',
      priority: 'high',
      owner: 'COO',
      dueDate: '5 days',
      expectedOutcome: 'Reduced returns',
      impact: '-18% return rate expected',
    },
    {
      id: '2',
      title: 'Improve Product Photography',
      description:
        'Add 360° views and fabric close-ups for color-sensitive items. Include "true color" badge on products with accurate photos.',
      priority: 'medium',
      owner: 'CMO',
      dueDate: '14 days',
      expectedOutcome: 'Better expectations',
      impact: '-12% color-related returns',
    },
    {
      id: '3',
      title: 'Proactive Outreach for High-Risk Orders',
      description:
        'Email customers within 24h of ordering flagged items with fit tips, size confirmation prompt, and easy exchange option.',
      priority: 'medium',
      owner: 'COO',
      dueDate: '7 days',
      expectedOutcome: 'More exchanges vs returns',
      impact: '25% exchange vs. return',
    },
  ],
  impact: {
    revenueImpact: 0,
    costImpact: -42000,
    roi: 0,
    description: 'Cost Savings: $42K in logistics costs',
  },
};

