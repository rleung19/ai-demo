import { KPIDetailData } from '@/app/lib/types/kpi';

export const kpi7SupplyChainData: KPIDetailData = {
  metadata: {
    id: 7,
    title: 'Supply Chain Lead Time Risk',
    owners: ['COO', 'CFO'],
    predictionHorizon: '14-42 Days',
    modelType: 'Multi-Signal Risk Model',
    trainingData: '24 months supplier performance + external signals',
    confidence: 76,
    lastUpdate: 'January 1, 2026',
    dataSources: [
      'Port congestion data',
      'Weather patterns',
      'Factory capacity',
      'Historical lead times',
      'Supplier performance',
    ],
  },
  alert: {
    icon: '🚢',
    title: '35% Probability of Major Shipment Delay',
    description:
      'Vietnam supplier (Supplier A) showing signs of potential 7-day delay. Emergency air freight costs: $110K. Port congestion and factory capacity constraints detected.',
  },
  metrics: [
    {
      label: 'Delay Probability',
      value: '35%',
      trend: 'neutral',
      color: 'amber',
    },
    {
      label: 'Expected Delay',
      value: '+7 days',
      trend: 'up',
      color: 'amber',
    },
    {
      label: 'Emergency Cost',
      value: '$110K',
      trend: 'neutral',
      color: 'rose',
    },
    {
      label: 'Model Confidence',
      value: '76%',
      trend: 'neutral',
      color: 'amber',
    },
  ],
  chartData: {
    labels: ['Supplier A (Vietnam)', 'Supplier B (China)', 'Supplier C (India)', 'Supplier D (Portugal)'],
    datasets: [
      {
        label: 'Delay Probability %',
        data: [35, 8, 12, 5],
        backgroundColor: ['#f59e0b', '#10b981', '#10b981', '#10b981'],
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
        max: 50,
        ticks: { callback: (v: any) => v + '%' },
      },
      y: { grid: { display: false } },
    },
  },
  tableData: [
    {
      supplier: 'Supplier A (Primary)',
      location: 'Vietnam',
      onTimeRate: '82%',
      delayProbability: '35%',
      impact: '$110K',
      status: '⚠️ Monitor',
    },
    {
      supplier: 'Supplier B',
      location: 'China',
      onTimeRate: '94%',
      delayProbability: '8%',
      impact: '$25K',
      status: '✅ Healthy',
    },
    {
      supplier: 'Supplier C',
      location: 'India',
      onTimeRate: '91%',
      delayProbability: '12%',
      impact: '$18K',
      status: '✅ Healthy',
    },
    {
      supplier: 'Supplier D',
      location: 'Portugal',
      onTimeRate: '96%',
      delayProbability: '5%',
      impact: '$8K',
      status: '✅ Healthy',
    },
  ],
  insight: {
    title: '🧠 AI Model Insight',
    content:
      'Supply chain risk model integrates port congestion data, weather patterns, and factory capacity signals. Vietnam port (Ho Chi Minh) showing 23% above-normal container dwell times. Recommend preemptive air freight booking for critical SKUs.',
    type: 'warning',
  },
  actions: [
    {
      id: '1',
      title: 'Alert Secondary Supplier (China)',
      description:
        "Prepare backup order for critical 8 SKUs with Supplier B. 21-day lead time vs. Supplier A's current 35+ days. Reserve capacity now.",
      priority: 'high',
      owner: 'COO',
      dueDate: 'TODAY',
      expectedOutcome: 'Risk mitigation',
      impact: 'Mitigates $85K stockout risk',
    },
    {
      id: '2',
      title: 'Increase Safety Stock for High-Risk Categories',
      description:
        'Add 2-week buffer inventory for all Vietnam-sourced items. Estimated working capital increase: $180K.',
      priority: 'medium',
      owner: 'COO',
      dueDate: '7 days',
      expectedOutcome: 'Stockout prevention',
      impact: 'Eliminates stockout risk',
    },
    {
      id: '3',
      title: 'Book Priority Air Freight Lanes',
      description:
        'Lock in air freight capacity with DHL/FedEx for emergency shipments. Negotiate volume rates for potential $110K shipment.',
      priority: 'medium',
      owner: 'COO',
      dueDate: '5 days',
      expectedOutcome: 'Faster delivery',
      impact: '15% cost reduction',
    },
  ],
  impact: {
    revenueImpact: 85000,
    costImpact: 110000,
    roi: -23,
    description: 'Risk Mitigation Cost: $110K, Protected Revenue: $85K',
  },
};

