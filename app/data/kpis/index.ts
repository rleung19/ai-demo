'use client';

import { kpi1ChurnRiskData } from '../synthetic/kpi1-churn-risk';
import { kpi2StockoutRiskData } from '../synthetic/kpi2-stockout-risk';
import { kpi3PriceElasticityData } from '../synthetic/kpi3-price-elasticity';
import { kpi4CACPaybackData } from '../synthetic/kpi4-cac-payback';
import { kpi5ReturnRateData } from '../synthetic/kpi5-return-rate';
import { kpi6EmailDecayData } from '../synthetic/kpi6-email-decay';
import { kpi7SupplyChainData } from '../synthetic/kpi7-supply-chain';
import { kpi8ConversionAnomalyData } from '../synthetic/kpi8-conversion-anomaly';
import { kpi9CLVTrajectoryData } from '../synthetic/kpi9-clv-trajectory';
import { kpi10DemandForecastData } from '../synthetic/kpi10-demand-forecast';
import { KPIDetailData } from '@/app/lib/types/kpi';
import {
  getChurnSummary,
  getChurnCohorts,
  getChurnMetrics,
  getChurnChartData,
} from '@/app/lib/api/churn-api';
import { transformChurnDataToKPI } from '@/app/lib/api/churn-data-transformer';

// KPI data registry - static data for KPIs 2-10
export const kpiDataRegistry: Record<number, KPIDetailData> = {
  2: kpi2StockoutRiskData,
  3: kpi3PriceElasticityData,
  4: kpi4CACPaybackData,
  5: kpi5ReturnRateData,
  6: kpi6EmailDecayData,
  7: kpi7SupplyChainData,
  8: kpi8ConversionAnomalyData,
  9: kpi9CLVTrajectoryData,
  10: kpi10DemandForecastData,
};

// Cache for KPI #1 data (churn)
let churnDataCache: KPIDetailData | null = null;
let churnDataCacheTime: number = 0;
const CACHE_TTL = 60000; // 1 minute

/**
 * Get KPI data - fetches from API for KPI #1, uses static data for others
 * Task 5.2: Fetch from API with fallback to static data
 */
export async function getKPIData(kpiId: number): Promise<KPIDetailData | null> {
  // KPI #1 (Churn) - fetch from API
  if (kpiId === 1) {
    // Check cache first
    const now = Date.now();
    if (churnDataCache && now - churnDataCacheTime < CACHE_TTL) {
      return churnDataCache;
    }

    try {
      // Fetch all churn data in parallel
      const [summary, cohorts, metrics, chartData] = await Promise.all([
        getChurnSummary(),
        getChurnCohorts(),
        getChurnMetrics(),
        getChurnChartData('distribution'),
      ]);

      // Transform API data to KPI format
      const transformedData = transformChurnDataToKPI(
        summary,
        cohorts,
        metrics,
        chartData,
        false // Not using fallback
      );

      // Update cache
      churnDataCache = transformedData;
      churnDataCacheTime = now;

      return transformedData;
    } catch (error) {
      console.error('Failed to fetch churn data from API:', error);
      // Fallback to static data
      const fallbackData = transformChurnDataToKPI(
        null,
        null,
        null,
        null,
        true // Using fallback
      );
      return fallbackData;
    }
  }

  // Other KPIs - use static data
  return kpiDataRegistry[kpiId] || null;
}
