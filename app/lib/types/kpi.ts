// KPI Types and Interfaces

export type ExecutiveRole = 'CFO' | 'COO' | 'CMO';

export type RiskLevel = 'low' | 'medium' | 'high';

export type TrendDirection = 'up' | 'down' | 'neutral';

export interface KPIMetadata {
  id: number;
  title: string;
  owners: ExecutiveRole[];
  predictionHorizon: string;
  modelType: string;
  trainingData: string;
  confidence: number;
  lastUpdate: string;
  dataSources: string[];
}

export interface MetricCard {
  label: string;
  value: string | number;
  trend?: TrendDirection;
  trendValue?: string;
  color: 'emerald' | 'amber' | 'rose' | 'teal' | 'blue';
}

export interface RecommendedAction {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  owner: ExecutiveRole;
  dueDate: string;
  expectedOutcome: string;
  impact?: string;
}

export interface BusinessImpact {
  revenueImpact: number;
  costImpact: number;
  roi?: number;
  description?: string;
}

export interface AlertBanner {
  icon: string;
  title: string;
  description: string;
}

export interface CohortCard {
  name: string;
  value: string | number;
  label: string;
  riskLevel?: RiskLevel;
}

export interface InsightBox {
  title: string;
  content: string;
  type?: 'info' | 'success' | 'warning';
}

export interface KPIDetailData {
  metadata: KPIMetadata;
  alert?: AlertBanner;
  metrics: MetricCard[];
  chartData: any; // Chart.js data structure
  chartOptions?: any; // Chart.js options
  tableData?: any[];
  cohorts?: CohortCard[];
  insight?: InsightBox;
  actions: RecommendedAction[];
  impact?: BusinessImpact;
}

