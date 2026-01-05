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

// KPI data registry - all 10 KPIs
export const kpiDataRegistry: Record<number, KPIDetailData> = {
  1: kpi1ChurnRiskData,
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

export function getKPIData(kpiId: number): KPIDetailData | null {
  return kpiDataRegistry[kpiId] || null;
}
