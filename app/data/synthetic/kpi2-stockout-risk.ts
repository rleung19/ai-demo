import { KPIDetailData } from '@/app/lib/types/kpi';

export const kpi2StockoutRiskData: KPIDetailData = {
  metadata: {
    id: 2,
    title: 'Stockout Risk Probability',
    owners: ['COO', 'CFO'],
    predictionHorizon: '14-28 Days',
    modelType: 'Prophet + LSTM Ensemble',
    trainingData: '24 months sales velocity + seasonal patterns',
    confidence: 89,
    lastUpdate: 'January 1, 2026',
    dataSources: [
      'Daily sales velocity',
      'Trend acceleration',
      'Seasonality',
      'Promotional calendar',
      'Social media signals',
    ],
  },
  alert: {
    icon: '🚨',
    title: '18 SKUs at Critical Stockout Risk',
    description:
      'AI predicts $85K revenue at risk in next 18 days. Summer Dress Charcoal (S-L) has 87% stockout probability within 18 days—expedited reorder recommended.',
  },
  metrics: [
    {
      label: 'SKUs at Risk',
      value: 18,
      trend: 'up',
      trendValue: '↑ 4 new this week',
      color: 'rose',
    },
    {
      label: 'Revenue at Risk',
      value: '$85K',
      trend: 'neutral',
      color: 'rose',
    },
    {
      label: 'Days to First Stockout',
      value: 18,
      trend: 'neutral',
      color: 'amber',
    },
    {
      label: 'Model Confidence',
      value: '89%',
      trend: 'neutral',
      color: 'teal',
    },
  ],
  chartData: {
    labels: ['Dresses', 'Outerwear', 'Accessories', 'Shoes', 'Basics', 'Activewear'],
    datasets: [
      {
        label: 'Days to Stockout',
        data: [18, 12, 21, 24, 28, 35],
        backgroundColor: ['#f43f5e', '#f43f5e', '#f59e0b', '#f59e0b', '#10b981', '#10b981'],
        borderRadius: 6,
      },
    ],
  },
  chartOptions: {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: { display: false },
    },
    scales: {
      x: {
        grid: { display: true },
        max: 40,
        ticks: { callback: (v: any) => v + ' days' },
      },
      y: { grid: { display: false } },
    },
  },
  cohorts: [
    {
      name: 'Dresses',
      value: 5,
      label: 'SKUs at risk • $52K impact',
      riskLevel: 'high',
    },
    {
      name: 'Outerwear',
      value: 4,
      label: 'SKUs at risk • $18K impact',
      riskLevel: 'medium',
    },
    {
      name: 'Accessories',
      value: 3,
      label: 'SKUs at risk • $8K impact',
      riskLevel: 'medium',
    },
    {
      name: 'Shoes',
      value: 2,
      label: 'SKUs at risk • $4K impact',
      riskLevel: 'low',
    },
  ],
  tableData: [
    {
      sku: 'Summer Dress Charcoal S-L',
      category: 'Dresses',
      daysToStockout: '18 days',
      riskLevel: '87%',
      weeklySales: '142 units',
      revenueImpact: '$40,200',
    },
    {
      sku: 'Linen Blazer Navy M-XL',
      category: 'Outerwear',
      daysToStockout: '12 days',
      riskLevel: '92%',
      weeklySales: '86 units',
      revenueImpact: '$18,400',
    },
    {
      sku: 'Silk Scarf Floral Print',
      category: 'Accessories',
      daysToStockout: '21 days',
      riskLevel: '68%',
      weeklySales: '210 units',
      revenueImpact: '$12,600',
    },
    {
      sku: 'Strappy Heel Nude 36-40',
      category: 'Shoes',
      daysToStockout: '24 days',
      riskLevel: '54%',
      weeklySales: '68 units',
      revenueImpact: '$8,160',
    },
    {
      sku: 'Cotton Tee White XS-S',
      category: 'Basics',
      daysToStockout: '28 days',
      riskLevel: '45%',
      weeklySales: '320 units',
      revenueImpact: '$5,600',
    },
  ],
  insight: {
    title: '🧠 AI Model Insight',
    content:
      'The stockout prediction model (LSTM time-series) factors in historical sales velocity, seasonality, social media trending signals, and supplier lead times. Summer Dress Charcoal saw 340% increase in Instagram mentions this week, driving the elevated risk score. Recommend immediate expedited order.',
    type: 'warning',
  },
  actions: [
    {
      id: '1',
      title: 'Expedite Summer Dress Charcoal Order',
      description:
        'Contact secondary supplier (Vietnam) for 21-day expedited delivery. Current primary supplier lead time is 35 days—too slow. Cost: $2,400 premium for air freight.',
      priority: 'high',
      owner: 'COO',
      dueDate: 'TODAY',
      expectedOutcome: 'Prevents stockout',
      impact: 'Saves $40K revenue',
    },
    {
      id: '2',
      title: 'Reallocate Inventory from Retail Partners',
      description:
        'Transfer 45 units of Linen Blazer Navy from Nordstrom allocation (lower velocity) to direct e-commerce channel.',
      priority: 'high',
      owner: 'COO',
      dueDate: '3 days',
      expectedOutcome: 'Extends runway',
      impact: '+12 days runway',
    },
    {
      id: '3',
      title: 'Increase Safety Stock Levels for Trending Items',
      description:
        'Raise reorder points by 30% for all items with >50% stockout risk. Update procurement system parameters.',
      priority: 'medium',
      owner: 'COO',
      dueDate: '7 days',
      expectedOutcome: 'Prevents future stockouts',
      impact: '-65% future stockout risk',
    },
    {
      id: '4',
      title: 'Enable AI Auto-Reorder for High-Velocity SKUs',
      description:
        'Activate automated reorder triggers when inventory falls below AI-calculated safety stock thresholds. Currently 12 SKUs eligible.',
      priority: 'low',
      owner: 'COO',
      dueDate: '14 days',
      expectedOutcome: 'Automates reordering',
      impact: 'Reduces manual intervention 80%',
    },
  ],
  impact: {
    revenueImpact: 85000,
    costImpact: 2400,
    roi: 3442,
    description: 'Avoided Lost Sales: $72,000',
  },
};
