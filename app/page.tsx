'use client';

import { useState, useEffect, useRef } from 'react';
import KPIDetailModal from './components/kpi-detail-modal/kpi-detail-modal';
import KPICard from './components/kpi-card/kpi-card';
import { getKPIData } from './data/kpis';
import { KPIDetailData } from './lib/types/kpi';

// KPI card data for the main dashboard
const kpiCards = [
  {
    id: 1,
    title: 'Churn Risk Score (Cohort)',
    owners: ['CMO', 'COO'],
    horizon: '30-60 Days',
    primaryMetric: '247',
    primaryLabel: 'At-Risk Customers',
    secondaryMetric: '68%',
    secondaryLabel: 'Avg Risk Score',
    primaryTrend: '↑ 12 from last week',
    secondaryTrend: '↓ 3% improved',
    status: 'alert' as const,
    confidence: 82,
    chartType: 'line' as const,
  },
  {
    id: 2,
    title: 'Stockout Risk Probability',
    owners: ['COO', 'CFO'],
    horizon: '14-28 Days',
    primaryMetric: '18',
    primaryLabel: 'SKUs at Risk',
    secondaryMetric: '$85K',
    secondaryLabel: 'Revenue at Risk',
    primaryTrend: '↑ 4 new this week',
    secondaryTrend: 'in next 18 days',
    status: 'alert' as const,
    confidence: 89,
    chartType: 'bar' as const,
  },
  {
    id: 3,
    title: 'Price Elasticity Forecast',
    owners: ['CFO', 'CMO'],
    horizon: '7-14 Days',
    primaryMetric: '$79',
    primaryLabel: 'Optimal Price Point',
    secondaryMetric: '+8.5%',
    secondaryLabel: 'Revenue Lift',
    primaryTrend: 'vs. current $89',
    secondaryTrend: 'if optimized',
    status: 'normal' as const,
    confidence: 91,
    chartType: 'line' as const,
  },
  {
    id: 4,
    title: 'CAC Payback Period Trend',
    owners: ['CFO', 'CMO'],
    horizon: '30-60 Days',
    primaryMetric: '8.2',
    primaryLabel: 'Current Payback',
    secondaryMetric: '↓ 1.3',
    secondaryLabel: 'Trend',
    primaryTrend: 'months',
    secondaryTrend: 'improving',
    status: 'normal' as const,
    confidence: 88,
    chartType: 'line' as const,
  },
  {
    id: 5,
    title: 'Return Rate Predictor',
    owners: ['COO', 'CMO'],
    horizon: '10-21 Days',
    primaryMetric: '28%',
    primaryLabel: 'Predicted Rate',
    secondaryMetric: '12',
    secondaryLabel: 'Flagged Items',
    primaryTrend: 'vs. 22% target',
    secondaryTrend: 'need attention',
    status: 'alert' as const,
    confidence: 85,
    chartType: 'line' as const,
  },
  {
    id: 6,
    title: 'Email Engagement Decay',
    owners: ['CMO'],
    horizon: '14-30 Days',
    primaryMetric: '-0.8%',
    primaryLabel: 'Decay Rate',
    secondaryMetric: '2.4K',
    secondaryLabel: 'At-Risk Subs',
    primaryTrend: 'per week',
    secondaryTrend: 'predict churn',
    status: 'alert' as const,
    confidence: 79,
    chartType: 'line' as const,
  },
  {
    id: 7,
    title: 'Supply Chain Lead Time Risk',
    owners: ['COO', 'CFO'],
    horizon: '14-42 Days',
    primaryMetric: '35%',
    primaryLabel: 'Delay Probability',
    secondaryMetric: '$110K',
    secondaryLabel: 'Impact',
    primaryTrend: 'next shipment',
    secondaryTrend: 'emergency cost',
    status: 'alert' as const,
    confidence: 76,
    chartType: 'bar' as const,
  },
  {
    id: 8,
    title: 'Conversion Anomaly Detector',
    owners: ['CMO', 'COO'],
    horizon: 'Real-time',
    primaryMetric: '2.8%',
    primaryLabel: 'Current CVR',
    secondaryMetric: '✓',
    secondaryLabel: 'Status',
    primaryTrend: 'normal range',
    secondaryTrend: 'No anomalies',
    status: 'normal' as const,
    confidence: 94,
    chartType: 'line' as const,
  },
  {
    id: 9,
    title: 'Customer CLV Trajectory',
    owners: ['CFO', 'CMO'],
    horizon: '90-180 Days',
    primaryMetric: '$342',
    primaryLabel: 'Avg CLV',
    secondaryMetric: '24%',
    secondaryLabel: 'High-Value %',
    primaryTrend: '↑ $28 YoY',
    secondaryTrend: 'of new cohort',
    status: 'normal' as const,
    confidence: 86,
    chartType: 'line' as const,
  },
  {
    id: 10,
    title: 'Demand Forecast + Confidence',
    owners: ['CFO', 'COO'],
    horizon: '14-42 Days',
    primaryMetric: '$8.2M',
    primaryLabel: 'Q1 Forecast',
    secondaryMetric: '92%',
    secondaryLabel: 'Accuracy',
    primaryTrend: '±$320K range',
    secondaryTrend: '↑ vs. baseline',
    status: 'normal' as const,
    confidence: 92,
    chartType: 'line' as const,
  },
];

export default function Home() {
  const [selectedKPI, setSelectedKPI] = useState<number | null>(null);
  const [kpiData, setKpiData] = useState<KPIDetailData | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [selectedTime, setSelectedTime] = useState<string>('30d');
  const [isDark, setIsDark] = useState(true);
  const [isLoadingKPI, setIsLoadingKPI] = useState(false);
  const [kpiError, setKpiError] = useState<string | null>(null);
  const [kpi1Data, setKpi1Data] = useState<KPIDetailData | null>(null);
  const [isLoadingKPI1, setIsLoadingKPI1] = useState(true);
  const [usingFallbackData, setUsingFallbackData] = useState(false);
  
  // Use ref to prevent double calls in StrictMode
  const hasFetchedKPI1 = useRef(false);
  const isFetchingKPI1 = useRef(false);

  // Theme toggle handler
  useEffect(() => {
    // Check initial theme preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setIsDark(prefersDark);
    if (!prefersDark) {
      document.documentElement.classList.add('light');
    }

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      setIsDark(e.matches);
      if (!e.matches) {
        document.documentElement.classList.add('light');
      } else {
        document.documentElement.classList.remove('light');
      }
    };
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const toggleTheme = () => {
    const newIsDark = !isDark;
    setIsDark(newIsDark);
    document.documentElement.classList.toggle('light');
  };

  // Load KPI #1 data on mount (Task 5.3)
  // Simple StrictMode-safe guard: per-component refs only
  useEffect(() => {
    // Prevent duplicate calls in development StrictMode (double-mount)
    if (hasFetchedKPI1.current || isFetchingKPI1.current) {
      return;
    }

    let cancelled = false;
    isFetchingKPI1.current = true;

    async function loadKPI1Data() {
      setIsLoadingKPI1(true);
      setKpiError(null);

      try {
        const data = await getKPIData(1, false);
        if (!cancelled) {
          setKpi1Data(data);
          setUsingFallbackData(data?.metadata.note?.includes('fallback') || false);
          hasFetchedKPI1.current = true;
        }
      } catch (error) {
        if (!cancelled) {
          console.error('Failed to load KPI #1 data:', error);
          setKpiError('Failed to load churn data');
          try {
            const fallbackData = await getKPIData(1);
            if (fallbackData) {
              setKpi1Data(fallbackData);
              setUsingFallbackData(true);
            }
          } catch {
            // Ignore fallback errors
          }
        }
      } finally {
        if (!cancelled) {
          setIsLoadingKPI1(false);
        }
        isFetchingKPI1.current = false;
      }
    }

    loadKPI1Data();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleKPIClick = async (kpiId: number) => {
    // For KPI #1, use already-fetched data if available
    if (kpiId === 1 && kpi1Data) {
      setKpiData(kpi1Data);
      setSelectedKPI(kpiId);
      setIsModalOpen(true);
      return;
    }
    
    // For other KPIs or if KPI #1 data not available, fetch it
    setIsLoadingKPI(true);
    setKpiError(null);
    try {
      const data = await getKPIData(kpiId);
      if (data) {
        setKpiData(data);
        setSelectedKPI(kpiId);
        setIsModalOpen(true);
      }
    } catch (error) {
      console.error('Failed to load KPI data:', error);
      setKpiError('Failed to load KPI data');
    } finally {
      setIsLoadingKPI(false);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedKPI(null);
    setKpiData(null);
  };

  // Helper function to extract minimum days from horizon string
  const getMinDaysFromHorizon = (horizon: string): number => {
    if (horizon.toLowerCase() === 'real-time') return 0;
    
    // Extract numbers from horizon string (e.g., "7-14 Days" -> 7, "60-90 Days" -> 60)
    const match = horizon.match(/(\d+)/);
    return match ? parseInt(match[1], 10) : Infinity;
  };

  // Filter KPIs by role and time period
  const filteredKPIs = kpiCards.filter((kpi) => {
    // Role filter
    const roleMatch = selectedRole === 'all' || 
      kpi.owners.some((owner) => owner.toLowerCase() === selectedRole.toLowerCase());
    
    if (!roleMatch) return false;

    // Time filter
    const minDays = getMinDaysFromHorizon(kpi.horizon);
    
    switch (selectedTime) {
      case '7d':
        // Show KPIs with horizons starting at 7 days or less
        return minDays <= 7;
      case '30d':
        // Show KPIs with horizons starting at 30 days or less
        return minDays <= 30;
      case '90d':
        // Show all KPIs (90d is the longest filter)
        return true;
      default:
        return true;
    }
  });

  // Generate mini chart data for each KPI - matching HTML file exactly
  const getMiniChartData = (kpiId: number, chartType: 'line' | 'bar') => {
    const labels7 = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7'];
    
    switch (kpiId) {
      case 1: // Churn Risk - line chart showing risk trend
        return {
          labels: labels7,
          datasets: [
            {
              data: [52, 58, 55, 62, 65, 68, 68],
              borderColor: '#f43f5e', // rose
              backgroundColor: 'rgba(244, 63, 94, 0.1)',
              fill: true,
              borderWidth: 2,
            },
          ],
        };
      
      case 2: // Stockout Risk - bar chart showing increasing risk
        return {
          labels: labels7,
          datasets: [
            {
              data: [8, 10, 12, 14, 15, 17, 18],
              backgroundColor: '#f59e0b', // amber
              borderRadius: 4,
            },
          ],
        };
      
      case 3: // Price Elasticity - line chart showing demand curve
        return {
          labels: ['$69', '$74', '$79', '$84', '$89', '$94'],
          datasets: [
            {
              data: [180, 150, 128, 95, 72, 45],
              borderColor: '#10b981', // emerald
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              fill: true,
              borderWidth: 2,
            },
          ],
        };
      
      case 4: // CAC Payback - line chart showing improving trend
        return {
          labels: labels7,
          datasets: [
            {
              data: [10.2, 9.8, 9.5, 9.1, 8.8, 8.5, 8.2],
              borderColor: '#14b8a6', // teal
              backgroundColor: 'rgba(20, 184, 166, 0.1)',
              fill: true,
              borderWidth: 2,
            },
          ],
        };
      
      case 5: // Return Rate - line chart showing increasing rate
        return {
          labels: labels7,
          datasets: [
            {
              data: [22, 23, 24, 25, 26, 27, 28],
              borderColor: '#f59e0b', // amber
              backgroundColor: 'rgba(245, 158, 11, 0.1)',
              fill: true,
              borderWidth: 2,
            },
          ],
        };
      
      case 6: // Email Decay - line chart showing declining engagement
        return {
          labels: labels7,
          datasets: [
            {
              data: [42, 41, 40, 39, 38, 37, 36],
              borderColor: '#f97316', // coral
              backgroundColor: 'rgba(249, 115, 22, 0.1)',
              fill: true,
              borderWidth: 2,
            },
          ],
        };
      
      case 7: // Supply Chain - bar chart showing supplier risk
        return {
          labels: ['Supplier A', 'Supplier B', 'Supplier C'],
          datasets: [
            {
              data: [35, 18, 12],
              backgroundColor: ['#f59e0b', '#14b8a6', '#10b981'], // amber, teal, emerald
              borderRadius: 4,
            },
          ],
        };
      
      case 8: // Conversion Anomaly - line chart showing stable CVR
        return {
          labels: labels7,
          datasets: [
            {
              data: [2.6, 2.7, 2.8, 2.7, 2.8, 2.9, 2.8],
              borderColor: '#10b981', // emerald
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              fill: true,
              borderWidth: 2,
            },
          ],
        };
      
      case 9: // CLV Trajectory - line chart showing growth
        return {
          labels: ['Q1', 'Q2', 'Q3', 'Q4'],
          datasets: [
            {
              data: [298, 312, 328, 342],
              borderColor: '#3b82f6', // blue
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              fill: true,
              borderWidth: 2,
            },
          ],
        };
      
      case 10: // Demand Forecast - line chart with forecast and actual
        return {
          labels: ['Jan', 'Feb', 'Mar'],
          datasets: [
            {
              label: 'Forecast',
              data: [2.6, 2.8, 2.8],
              borderColor: '#8b5cf6', // violet
              backgroundColor: 'rgba(139, 92, 246, 0.1)',
              fill: true,
              borderWidth: 2,
            },
            {
              label: 'Actual',
              data: [2.5, 2.7, null],
              borderColor: '#10b981', // emerald
              borderWidth: 2,
              borderDash: [5, 5],
            },
          ],
        };
      
      default:
        return {
          labels: labels7,
          datasets: [
            {
              data: [52, 58, 55, 62, 65, 68, 68],
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              fill: true,
              borderWidth: 2,
            },
          ],
        };
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
      <div className="mx-auto px-4 py-6" style={{ maxWidth: '1600px' }}>
        {/* Header */}
        <header className="flex items-center justify-between mb-6 flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-blue-500 rounded-xl flex items-center justify-center font-bold text-white text-lg">
              AI
            </div>
            <div>
              <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                AI/ML Executive Dashboard
              </h1>
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                B2C Fashion E-commerce • January 2026
              </p>
            </div>
          </div>

          {/* Filter Bar */}
          <div className="flex items-center gap-3 flex-wrap">
            {/* Role Filter */}
            <div
              className="flex rounded-xl p-1 border"
              style={{
                backgroundColor: 'var(--bg-card)',
                borderColor: 'var(--border-color)',
              }}
            >
              {(['all', 'cfo', 'coo', 'cmo'] as const).map((role) => (
                <button
                  key={role}
                  onClick={() => setSelectedRole(role)}
                  className="px-4 py-2 text-sm font-semibold rounded-lg transition-colors"
                  style={
                    selectedRole === role
                      ? {
                          background: 'linear-gradient(135deg, #14b8a6 0%, #3b82f6 100%)',
                          color: '#ffffff',
                        }
                      : {
                          color: 'var(--text-secondary)',
                        }
                  }
                  onMouseEnter={(e) => {
                    if (selectedRole !== role) {
                      e.currentTarget.style.color = 'var(--text-primary)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedRole !== role) {
                      e.currentTarget.style.color = 'var(--text-secondary)';
                    }
                  }}
                >
                  {role === 'all' ? 'All KPIs' : role.toUpperCase()}
                </button>
              ))}
            </div>

            {/* Time Filter */}
            <div
              className="flex rounded-xl p-1 border"
              style={{
                backgroundColor: 'var(--bg-card)',
                borderColor: 'var(--border-color)',
              }}
            >
              {(['7d', '30d', '90d'] as const).map((time) => (
                <button
                  key={time}
                  onClick={() => setSelectedTime(time)}
                  className="px-3 py-2 text-sm font-medium rounded-lg transition-colors"
                  style={
                    selectedTime === time
                      ? {
                          backgroundColor: 'var(--bg-secondary)',
                          color: 'var(--text-primary)',
                        }
                      : {
                          color: 'var(--text-secondary)',
                        }
                  }
                  onMouseEnter={(e) => {
                    if (selectedTime !== time) {
                      e.currentTarget.style.color = 'var(--text-primary)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedTime !== time) {
                      e.currentTarget.style.color = 'var(--text-secondary)';
                    }
                  }}
                >
                  {time.toUpperCase()}
                </button>
              ))}
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="w-11 h-11 rounded-lg flex items-center justify-center text-lg transition-colors"
              style={{
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-secondary)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)';
                e.currentTarget.style.color = 'var(--text-primary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg-card)';
                e.currentTarget.style.color = 'var(--text-secondary)';
              }}
              aria-label="Toggle theme"
            >
              {isDark ? '☀' : '☾'}
            </button>
          </div>
        </header>

        {/* Alert Banner */}
        <div
          className="rounded-2xl p-5 mb-6 flex items-center gap-4"
          style={{
            background: 'linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(244, 63, 94, 0.15) 100%)',
            border: '1px solid rgba(249, 115, 22, 0.3)',
          }}
        >
          <div className="w-12 h-12 bg-gradient-to-br from-amber-500 to-rose-500 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">
            ⚠️
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold mb-1" style={{ color: '#f59e0b' }}>
              5 KPIs Require Attention
            </h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Churn Risk, Stockout Probability, Return Rate, Email Decay, and Supply Chain Risk are
              showing yellow alerts. Immediate action recommended.
            </p>
          </div>
          <div className="flex gap-2">
            <button
              className="px-4 py-2 bg-gradient-to-r from-amber-500 to-rose-500 text-white rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity"
            >
              Review Now
            </button>
            <button
              className="px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
              style={{
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-secondary)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg-card)';
              }}
            >
              Dismiss
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div
            className="rounded-2xl p-6 border"
            style={{
              backgroundColor: 'var(--bg-card)',
              borderColor: 'var(--border-color)',
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>
                Total Revenue Impact
              </span>
              <span className="px-2 py-1 text-xs font-semibold rounded" style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#10b981' }}>
                On Track
              </span>
            </div>
            <div className="text-3xl font-bold font-mono mb-1" style={{ color: 'var(--text-primary)' }}>
              $2.4M
            </div>
            <div className="text-sm text-emerald-500 flex items-center gap-1">
              <span>↑</span> 12.3% vs. last quarter
            </div>
          </div>
          <div
            className="rounded-2xl p-6 border"
            style={{
              backgroundColor: 'var(--bg-card)',
              borderColor: 'var(--border-color)',
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>
                Cost Savings
              </span>
              <span className="px-2 py-1 text-xs font-semibold rounded" style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#10b981' }}>
                Exceeding
              </span>
            </div>
            <div className="text-3xl font-bold font-mono mb-1" style={{ color: 'var(--text-primary)' }}>
              $485K
            </div>
            <div className="text-sm text-emerald-500 flex items-center gap-1">
              <span>↑</span> 8.7% efficiency gain
            </div>
          </div>
          <div
            className="rounded-2xl p-6 border"
            style={{
              backgroundColor: 'var(--bg-card)',
              borderColor: 'var(--border-color)',
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>
                At-Risk Revenue
              </span>
              <span className="px-2 py-1 text-xs font-semibold rounded" style={{ backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#f59e0b' }}>
                Monitor
              </span>
            </div>
            <div className="text-3xl font-bold font-mono mb-1" style={{ color: 'var(--text-primary)' }}>
              {kpi1Data?.impact?.revenueImpact
                ? `$${Math.abs(kpi1Data.impact.revenueImpact / 1000).toFixed(0)}K`
                : '$320K'}
            </div>
            <div className="text-sm text-rose-500 flex items-center gap-1">
              <span>↓</span> Action needed in 14 days
            </div>
          </div>
          <div
            className="rounded-2xl p-6 border"
            style={{
              backgroundColor: 'var(--bg-card)',
              borderColor: 'var(--border-color)',
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>
                AI Confidence
              </span>
              <span className="px-2 py-1 text-xs font-semibold rounded" style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#10b981' }}>
                High
              </span>
            </div>
            <div className="text-3xl font-bold font-mono mb-1" style={{ color: 'var(--text-primary)' }}>
              87%
            </div>
            <div className="text-sm flex items-center gap-1" style={{ color: 'var(--text-muted)' }}>
              <span>→</span> Average across all models
            </div>
          </div>
        </div>

        {/* KPI Grid */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-4">
            <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
              10 Leading AI/ML KPIs
            </h2>
            <span
              className="px-3 py-1 rounded-full text-xs font-semibold"
              style={{
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                color: 'var(--accent-violet)',
              }}
            >
              Predictive Indicators
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredKPIs.map((kpi) => {
              // Task 5.3: Use real-time data for KPI #1
              if (kpi.id === 1) {
                if (isLoadingKPI1) {
                  return (
                    <div
                      key={kpi.id}
                      className="rounded-2xl p-6 border animate-pulse"
                      style={{
                        backgroundColor: 'var(--bg-card)',
                        borderColor: 'var(--border-color)',
                      }}
                    >
                      <div className="h-4 bg-gray-300 rounded w-3/4 mb-4"></div>
                      <div className="h-8 bg-gray-300 rounded w-1/2 mb-2"></div>
                      <div className="h-4 bg-gray-300 rounded w-2/3"></div>
                    </div>
                  );
                }

                // Use real-time data from API
                const realTimeKPI = kpi1Data
                  ? {
                      ...kpi,
                      primaryMetric:
                        kpi1Data.metrics[0]?.value != null
                          ? String(kpi1Data.metrics[0].value)
                          : kpi.primaryMetric,
                      primaryLabel: kpi1Data.metrics[0]?.label || kpi.primaryLabel,
                      secondaryMetric:
                        kpi1Data.metrics[1]?.value != null
                          ? String(kpi1Data.metrics[1].value)
                          : kpi.secondaryMetric,
                      secondaryLabel: kpi1Data.metrics[1]?.label || kpi.secondaryLabel,
                      confidence: kpi1Data.metadata.confidence || kpi.confidence,
                      status: (() => {
                        const rawValue = kpi1Data.metrics[0]?.value;
                        if (rawValue == null) return kpi.status;
                        const strValue = typeof rawValue === 'number' ? rawValue.toString() : rawValue;
                        const numeric = parseInt(strValue.replace(/,/g, ''), 10);
                        return Number.isFinite(numeric) && numeric > 1000 ? 'alert' as const : kpi.status;
                      })(),
                    }
                  : kpi;

                const miniChartData = kpi1Data?.chartData || getMiniChartData(kpi.id, kpi.chartType);
                const firstDataset = miniChartData.datasets?.[0] as any;
                const actualChartType = firstDataset?.borderColor !== undefined ? 'line' : 'bar';

                return (
                  <div key={kpi.id} className="relative">
                    {usingFallbackData && (
                      <div
                        className="absolute top-2 right-2 px-2 py-1 rounded text-xs font-semibold z-10"
                        style={{
                          backgroundColor: 'rgba(245, 158, 11, 0.2)',
                          color: '#f59e0b',
                        }}
                        title="Using cached data - API unavailable"
                      >
                        ⚠️ Cached
                      </div>
                    )}
                    <KPICard
                      {...realTimeKPI}
                      chartType={actualChartType}
                      chartData={miniChartData}
                      onClick={() => handleKPIClick(kpi.id)}
                    />
                  </div>
                );
              }

              // Other KPIs - use static data
              const miniChartData = getMiniChartData(kpi.id, kpi.chartType);
              const firstDataset = miniChartData.datasets?.[0] as any;
              const actualChartType = firstDataset?.borderColor !== undefined ? 'line' : 'bar';
              return (
                <KPICard
                  key={kpi.id}
                  {...kpi}
                  chartType={actualChartType}
                  chartData={miniChartData}
                  onClick={() => handleKPIClick(kpi.id)}
                />
              );
            })}
          </div>
        </div>
      </div>

      <KPIDetailModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        kpiData={kpiData}
      />
    </div>
  );
}
