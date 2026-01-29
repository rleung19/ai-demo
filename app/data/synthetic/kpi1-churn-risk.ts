import { KPIDetailData } from '@/app/lib/types/kpi';

export const kpi1ChurnRiskData: KPIDetailData = {
  metadata: {
    id: 1,
    title: 'Churn Risk Score (Cohort)',
    owners: ['CMO', 'COO'],
    predictionHorizon: '60-90 Days',
    modelType: 'XGBoost Binary Classification',
    trainingData: '24 months customer behavior data',
    confidence: 82,
    lastUpdate: 'January 1, 2026',
    dataSources: [
      'Login frequency',
      'Support tickets',
      'NPS sentiment',
      'Purchase velocity',
      'Email engagement',
      'Browse-to-cart ratio',
    ],
  },
  alert: {
    icon: '⚠️',
    title: '247 High-Value Customers at Risk',
    description:
      'AI model predicts $112K in LTV at risk within 60 days. VIP segment shows 68% churn probability, primarily driven by sizing issues and reduced email engagement.',
  },
  metrics: [
    {
      label: 'At-Risk Customers',
      value: 247,
      trend: 'up',
      trendValue: '↑ 12 from last week',
      color: 'rose',
    },
    {
      label: 'Avg Risk Score',
      value: '68%',
      trend: 'down',
      trendValue: '↓ 3% improved',
      color: 'amber',
    },
    {
      label: 'LTV at Risk',
      value: '$112K',
      trend: 'neutral',
      color: 'rose',
    },
    {
      label: 'Model Confidence',
      value: '82%',
      trend: 'neutral',
      color: 'teal',
    },
  ],
  chartData: {
    labels: ['VIP', 'Regular', 'New', 'Dormant', 'At-Risk'],
    datasets: [
      {
        label: 'Churn Probability %',
        data: [68, 42, 18, 85, 72],
        backgroundColor: ['#f43f5e', '#f59e0b', '#10b981', '#f43f5e', '#f97316'],
        borderRadius: 6,
      },
      {
        label: 'Customer Count (scaled)',
        data: [15, 52, 124, 10, 25],
        backgroundColor: 'rgba(59, 130, 246, 0.3)',
        borderColor: '#3b82f6',
        borderWidth: 2,
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
  cohorts: [
    {
      name: 'VIP Customers',
      value: '68%',
      label: '150 customers • $67.5K LTV',
      riskLevel: 'high',
    },
    {
      name: 'Regular Buyers',
      value: '42%',
      label: '520 customers • $28K LTV',
      riskLevel: 'medium',
    },
    {
      name: 'New Customers',
      value: '18%',
      label: '1,240 customers • $12K LTV',
      riskLevel: 'low',
    },
    {
      name: 'Dormant (60d+)',
      value: '85%',
      label: '97 customers • $4.5K LTV',
      riskLevel: 'high',
    },
  ],
  tableData: [
    {
      riskFactor: 'Returns rate > 20%',
      impactScore: '92%',
      affectedCustomers: 89,
      primarySegment: 'VIP, Regular',
    },
    {
      riskFactor: 'Email open rate < 20%',
      impactScore: '78%',
      affectedCustomers: 156,
      primarySegment: 'All segments',
    },
    {
      riskFactor: 'No Purchase in 45+ Days',
      impactScore: '65%',
      affectedCustomers: 203,
      primarySegment: 'Regular, Dormant',
    },
    {
      riskFactor: 'Customer service calls > 2',
      impactScore: '54%',
      affectedCustomers: 42,
      primarySegment: 'VIP',
    },
    {
      riskFactor: 'Cart abandonment rate > 50%',
      impactScore: '38%',
      affectedCustomers: 118,
      primarySegment: 'New, Regular',
    },
  ],
  insight: {
    title: '🧠 AI Model Insight',
    content:
      'The churn prediction model (XGBoost ensemble) identifies Returns rate > 20% + Email open rate < 20% + No Purchase in 45+ Days as the strongest predictors of churn. Recommend prioritizing VIP segment with personalized sizing guidance and exclusive re-engagement offers.',
    type: 'info',
  },
  actions: [
    {
      id: '1',
      title: 'Launch VIP Re-engagement Campaign',
      description:
        'Target 150 VIP customers with personalized 25% discount on their most-viewed categories. Include dedicated stylist consultation offer.',
      priority: 'high',
      owner: 'CMO',
      dueDate: '7 days',
      expectedOutcome: 'Rescue 10-15 customers (30% rate), preserve $20K-30K LTV',
      impact: '+$45K revenue recovery',
    },
    {
      id: '2',
      title: 'Address Returns rate > 20% for 89 Customers',
      description:
        'Proactive outreach to customers with returns rate > 20%. Offer free exchange, size guide consultation, and $20 credit for next purchase.',
      priority: 'high',
      owner: 'COO',
      dueDate: '5 days',
      expectedOutcome: 'Reduce complaint-driven churn by 25%',
      impact: '-18% return rate expected',
    },
    {
      id: '3',
      title: 'Win-back Email Sequence for Dormant Segment',
      description:
        'Deploy 4-email sequence for 97 dormant customers: "We miss you" → Product recommendations → Exclusive offer → Final reminder with urgency.',
      priority: 'medium',
      owner: 'CMO',
      dueDate: '10 days',
      expectedOutcome: '12-18% reactivation rate',
      impact: '12-18% reactivation rate',
    },
    {
      id: '4',
      title: 'High-Touch Outreach for Top 50 VIPs',
      description:
        'Personal phone calls from customer success team to highest-value at-risk customers. Collect feedback and offer exclusive preview access.',
      priority: 'low',
      owner: 'CMO',
      dueDate: 'Ongoing weekly',
      expectedOutcome: '85% retention for contacted',
      impact: '85% retention for contacted',
    },
  ],
  impact: {
    revenueImpact: 112350,
    costImpact: 8500,
    roi: 296,
    description: 'Net ROI: 296% (Recovery - Cost) / Cost',
  },
};
