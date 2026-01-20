/**
 * Churn Model API Client
 * Task 5.1: API client utility for fetching churn data from backend
 *
 * The frontend can be configured to use either:
 * 1. Next.js API Routes (same origin, port 3000)
 * 2. Express Standalone Server (separate server, port 3001)
 *
 * Configuration:
 * - Set NEXT_PUBLIC_API_URL environment variable to override
 * - Default behavior is controlled by the fallback value below
 *
 * Current default: Express server (http://localhost:3001)
 * To use Next.js API routes: Set NEXT_PUBLIC_API_URL='' or change fallback to ''
 *
 * See docs/API_SERVER_SWITCH.md for detailed switching instructions.
 */

// API Base URL Configuration
// - Empty string ('') = Use Next.js API routes (same origin)
// - URL (e.g., 'http://localhost:3001') = Use Express standalone server
// - Can be overridden via NEXT_PUBLIC_API_URL environment variable
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

export interface RiskFactor {
  riskFactor: string;
  impactScore: string;
  affectedCustomers: number;
  primarySegment: string;
}

export interface RiskFactorsResponse {
  riskFactors: RiskFactor[];
  lastUpdate: string;
}

export interface ApiError {
  error: string;
  message: string;
  fallback?: boolean;
}

/**
 * Fetch with timeout and retry logic.
 *
 * Now that we've identified browser-side timeouts as the main source of
 * duplicate calls, this helper is intentionally simple – no global
 * deduplication or cross-request state, just retries and a per-call timeout.
 */
async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retries = 3,
  timeout = 15000 // 15 seconds to comfortably cover DB latency
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
      if (
        attempt < retries &&
        (error.name === 'AbortError' || error.name === 'TypeError')
      ) {
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
  const callId = Math.random().toString(36).substring(7);
  console.log(`[getChurnSummary:${callId}] Called`);
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
  const callId = Math.random().toString(36).substring(7);
  console.log(`[getChurnCohorts:${callId}] Called`);
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
  const callId = Math.random().toString(36).substring(7);
  console.log(`[getChurnMetrics:${callId}] Called`);
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
 *
 * Simple coalescing: if a request for the same chart type is already in flight,
 * reuse the existing promise instead of firing a new HTTP request. This is a
 * lightweight form of request debouncing for chart data.
 */
let inFlightChartDataPromise: Promise<ChartData | null> | null = null;
let inFlightChartType: 'distribution' | 'cohort-trend' | null = null;

export async function getChurnChartData(
  type: 'distribution' | 'cohort-trend' = 'distribution'
): Promise<ChartData | null> {
  const callId = Math.random().toString(36).substring(7);
  console.log(`[getChurnChartData:${callId}] Called, type=${type}`);

  if (inFlightChartDataPromise && inFlightChartType === type) {
    console.log(
      `[getChurnChartData:${callId}] Reusing in-flight promise for type=${type}`
    );
    return inFlightChartDataPromise;
  }

  inFlightChartType = type;

  inFlightChartDataPromise = (async () => {
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
    } finally {
      inFlightChartDataPromise = null;
      inFlightChartType = null;
    }
  })();

  return inFlightChartDataPromise;
}

/**
 * Get churn risk factors
 */
export async function getChurnRiskFactors(): Promise<RiskFactorsResponse | null> {
  const callId = Math.random().toString(36).substring(7);
  console.log(`[getChurnRiskFactors:${callId}] Called`);
  try {
    const response = await fetchWithRetry(`${API_BASE_URL}/api/kpi/churn/risk-factors`);
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      if (error.fallback) {
        console.warn('API returned fallback data for risk factors');
      }
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch churn risk factors:', error);
    return null;
  }
}

/**
 * Check API health
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetchWithRetry(`${API_BASE_URL}/api/health`, {}, 1, 10000);  // Increased to 10 seconds
    if (!response.ok) return false;
    const health = await response.json();
    return health.status === 'healthy' && health.services?.database === 'connected';
  } catch (error) {
    return false;
  }
}
