/**
 * Churn Model API Client
 * Task 5.1: API client utility for fetching churn data from backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

export interface ChurnSummary {
  atRiskCount: number;
  totalCustomers: number;
  atRiskPercentage: number;
  averageRiskScore: number;
  totalLTVAtRisk: number;
  modelConfidence: number | null;
  lastUpdate: string | null;
  modelVersion: string | null;
}

export interface ChurnCohort {
  cohort: string;
  customerCount: number;
  atRiskCount: number;
  atRiskPercentage: number;
  averageRiskScore: number;
  ltvAtRisk: number;
}

export interface ChurnMetrics {
  modelId: string;
  modelName: string;
  modelVersion: string;
  modelType: string;
  modelConfidence: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  optimalThreshold: number;
  lastUpdate: string;
  trainingStats: {
    trainSamples: number;
    testSamples: number;
    featureCount: number;
  };
  status: string;
}

export interface ChartDataPoint {
  riskRange: string;
  customerCount: number;
  atRiskCount: number;
}

export interface ChartData {
  chartType: string;
  data: ChartDataPoint[];
}

export interface ApiError {
  error: string;
  message: string;
  fallback?: boolean;
}

/**
 * Fetch with timeout and retry logic
 */
/**
 * Fetch with timeout and retry logic
 * Task 5.6: Retry logic for failed API calls
 */
async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retries = 3,
  timeout = 5000
): Promise<Response> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      
      // Retry on 5xx errors
      if (response.status >= 500 && attempt < retries) {
        await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
        continue;
      }
      
      return response;
    } catch (error: any) {
      clearTimeout(timeoutId);
      lastError = error;
      
      // Retry on timeout or network error
      if (attempt < retries && (error.name === 'AbortError' || error.name === 'TypeError')) {
        await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
        continue;
      }
    }
  }
  
  throw lastError || new Error('Failed to fetch after retries');
}

/**
 * Get churn summary statistics
 */
export async function getChurnSummary(): Promise<ChurnSummary | null> {
  try {
    const response = await fetchWithRetry(`${API_BASE_URL}/api/kpi/churn/summary`);
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      if (error.fallback) {
        console.warn('API returned fallback data for summary');
      }
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch churn summary:', error);
    return null;
  }
}

/**
 * Get churn breakdown by cohorts
 */
export async function getChurnCohorts(): Promise<ChurnCohort[] | null> {
  try {
    const response = await fetchWithRetry(`${API_BASE_URL}/api/kpi/churn/cohorts`);
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      if (error.fallback) {
        console.warn('API returned fallback data for cohorts');
      }
      return null;
    }

    const data = await response.json();
    return data.cohorts || null;
  } catch (error) {
    console.error('Failed to fetch churn cohorts:', error);
    return null;
  }
}

/**
 * Get model metrics and confidence
 */
export async function getChurnMetrics(): Promise<ChurnMetrics | null> {
  try {
    const response = await fetchWithRetry(`${API_BASE_URL}/api/kpi/churn/metrics`);
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      if (error.fallback) {
        console.warn('API returned fallback data for metrics');
      }
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch churn metrics:', error);
    return null;
  }
}

/**
 * Get chart data for churn visualization
 */
export async function getChurnChartData(type: 'distribution' | 'cohort-trend' = 'distribution'): Promise<ChartData | null> {
  try {
    const response = await fetchWithRetry(
      `${API_BASE_URL}/api/kpi/churn/chart-data?type=${type}`
    );
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      if (error.fallback) {
        console.warn('API returned fallback data for chart');
      }
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch churn chart data:', error);
    return null;
  }
}

/**
 * Check API health
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetchWithRetry(`${API_BASE_URL}/api/health`, {}, 1, 3000);
    if (!response.ok) return false;
    const health = await response.json();
    return health.status === 'healthy' && health.services?.database === 'connected';
  } catch (error) {
    return false;
  }
}
