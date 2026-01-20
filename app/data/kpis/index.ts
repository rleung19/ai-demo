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
  getChurnRiskFactors,
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

// Shared cache for all KPI data (not just KPI #1)
const kpiDataCache: Map<number, { data: KPIDetailData; timestamp: number }> = new Map();
const CACHE_TTL = 60000; // 1 minute

// Cache for KPI #1 data (churn) - kept for backward compatibility
let churnDataCache: KPIDetailData | null = null;
let churnDataCacheTime: number = 0;

// Simple in-flight promise for KPI #1 (per-tab, client-side only)
let inFlightKPI1Promise: Promise<KPIDetailData | null> | null = null;

/**
 * Get KPI data - fetches from API for KPI #1, uses static data for others
 * Task 5.2: Fetch from API with fallback to static data
 * Optimized: Uses shared cache to avoid duplicate API calls
 */
export async function getKPIData(
  kpiId: number,
  forceRefresh = false
): Promise<KPIDetailData | null> {
  const now = Date.now();

  // KPI #1 (Churn) - fetch from API
  if (kpiId === 1) {
    // If a request is already in-flight and we're not forcing a refresh, reuse it
    if (inFlightKPI1Promise && !forceRefresh) {
      return inFlightKPI1Promise;
    }

    // Check cache first (per-tab, client-side only)
    if (!forceRefresh) {
      const cached = kpiDataCache.get(kpiId);
      if (cached && now - cached.timestamp < CACHE_TTL) {
        return cached.data;
      }

      if (churnDataCache && now - churnDataCacheTime < CACHE_TTL) {
        kpiDataCache.set(kpiId, { data: churnDataCache, timestamp: churnDataCacheTime });
        return churnDataCache;
      }
    }

    // No valid cache – create a new in-flight promise
    inFlightKPI1Promise = (async () => {
      try {
        const [summary, cohorts, metrics, chartData, riskFactorsResponse] =
          await Promise.all([
            getChurnSummary(),
            getChurnCohorts(),
            getChurnMetrics(),
            getChurnChartData('distribution'),
            getChurnRiskFactors(),
          ]);

        const transformedData = transformChurnDataToKPI(
          summary,
          cohorts,
          metrics,
          chartData,
          riskFactorsResponse?.riskFactors || null,
          false // Not using fallback
        );

        churnDataCache = transformedData;
        churnDataCacheTime = Date.now();
        kpiDataCache.set(kpiId, { data: transformedData, timestamp: Date.now() });

        return transformedData;
      } catch (error) {
        console.error('[KPI1] Failed to fetch churn data from API:', error);

        // Fallback to static data
        const fallbackData = transformChurnDataToKPI(
          null,
          null,
          null,
          null,
          null, // No risk factors in fallback
          true // Using fallback
        );
        return fallbackData;
      } finally {
        // Allow a new request next time
        inFlightKPI1Promise = null;
      }
    })();

    return inFlightKPI1Promise;
  }

  // Other KPIs - use static data
  const staticData = kpiDataRegistry[kpiId] || null;
  if (staticData) {
    kpiDataCache.set(kpiId, { data: staticData, timestamp: now });
  }
  return staticData;
}

/**
 * Clear cache for a specific KPI or all KPIs
 */
export function clearKPICache(kpiId?: number): void {
  if (kpiId) {
    kpiDataCache.delete(kpiId);
    if (kpiId === 1) {
      churnDataCache = null;
      churnDataCacheTime = 0;
    }
  } else {
    kpiDataCache.clear();
    churnDataCache = null;
    churnDataCacheTime = 0;
  }
}
