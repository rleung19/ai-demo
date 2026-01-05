import { KPIDetailData } from '@/app/lib/types/kpi';

export const kpi8ConversionAnomalyData: KPIDetailData = {
  metadata: {
    id: 8,
    title: 'Conversion Anomaly Detector',
    owners: ['CMO', 'COO'],
    predictionHorizon: 'Real-time',
    modelType: 'Statistical Process Control + ML',
    trainingData: '12 months conversion data',
    confidence: 94,
    lastUpdate: 'January 1, 2026',
    dataSources: [
      'Real-time CVR',
      'Payment gateway status',
      'Checkout funnel data',
      'Device/browser breakdown',
      'Geographic patterns',
    ],
  },
  metrics: [
    {
      label: 'Current CVR',
      value: '2.8%',
      trend: 'neutral',
      trendValue: 'normal range',
      color: 'emerald',
    },
    {
      label: 'Active Anomalies',
      value: 0,
      trend: 'neutral',
      color: 'emerald',
    },
    {
      label: 'Avg Detection Time',
      value: '<6h',
      trend: 'neutral',
      color: 'teal',
    },
    {
      label: 'Model Confidence',
      value: '94%',
      trend: 'neutral',
      color: 'teal',
    },
  ],
  chartData: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Conversion Rate %',
        data: [2.6, 2.7, 2.8, 2.7, 2.9, 3.1, 2.8],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 3,
      },
      {
        label: 'Expected Range (upper)',
        data: [3.2, 3.2, 3.2, 3.2, 3.2, 3.2, 3.2],
        borderColor: 'rgba(100, 116, 139, 0.3)',
        borderDash: [5, 5],
        borderWidth: 1,
        pointRadius: 0,
        fill: false,
      },
      {
        label: 'Expected Range (lower)',
        data: [2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2],
        borderColor: 'rgba(100, 116, 139, 0.3)',
        borderDash: [5, 5],
        borderWidth: 1,
        pointRadius: 0,
        fill: false,
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
        min: 1.5,
        max: 4,
        ticks: { callback: (v: any) => v + '%' },
      },
    },
  },
  tableData: [
    {
      channel: 'Direct',
      currentCvr: '4.2%',
      sevenDayAvg: '4.0%',
      trend: '↑ +0.2%',
      status: '✅ Normal',
    },
    {
      channel: 'Organic Search',
      currentCvr: '3.1%',
      sevenDayAvg: '2.9%',
      trend: '↑ +0.2%',
      status: '✅ Normal',
    },
    {
      channel: 'Paid Social',
      currentCvr: '1.8%',
      sevenDayAvg: '2.0%',
      trend: '↓ -0.2%',
      status: '⚡ Watch',
    },
    {
      channel: 'Email',
      currentCvr: '5.4%',
      sevenDayAvg: '5.2%',
      trend: '↑ +0.2%',
      status: '✅ Normal',
    },
    {
      channel: 'Affiliate',
      currentCvr: '2.4%',
      sevenDayAvg: '2.3%',
      trend: '↑ +0.1%',
      status: '✅ Normal',
    },
  ],
  insight: {
    title: '✅ System Status: All Clear',
    content:
      'No conversion anomalies detected in past 7 days. All payment gateways operational. Mobile and desktop CVR within normal bands. Last anomaly (Stripe timeout) detected and resolved 18 days ago.',
    type: 'success',
  },
  actions: [
    {
      id: '1',
      title: 'Continue Real-Time Monitoring',
      description:
        'AI anomaly detector running with 15-minute data refresh. Alerts trigger when CVR drops >15% below rolling 24h average.',
      priority: 'low',
      owner: 'COO',
      dueDate: 'Automated',
      expectedOutcome: 'Early detection',
      impact: 'Automated',
    },
    {
      id: '2',
      title: 'Watch Paid Social CVR',
      description:
        'Paid Social showing slight decline (-0.2%). Not anomalous yet but worth monitoring. May indicate creative fatigue or audience saturation.',
      priority: 'low',
      owner: 'CMO',
      dueDate: '3 days',
      expectedOutcome: 'Monitor trend',
      impact: 'Review in 3 days',
    },
    {
      id: '3',
      title: 'Weekly Checkout Audit',
      description:
        'Manual QA test of all payment methods (Visa, Mastercard, Amex, PayPal, Apple Pay, Shop Pay) every Monday.',
      priority: 'low',
      owner: 'COO',
      dueDate: 'Next: Monday 9AM',
      expectedOutcome: 'Quality assurance',
      impact: 'Next: Monday 9AM',
    },
  ],
  impact: {
    revenueImpact: 0,
    costImpact: 0,
    roi: 0,
    description: 'System Operating Normally',
  },
};

