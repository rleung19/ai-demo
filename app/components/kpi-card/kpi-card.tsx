'use client';

import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  Filler
);

interface KPICardProps {
  id: number;
  title: string;
  owners: string[];
  horizon: string;
  primaryMetric: string;
  primaryLabel: string;
  secondaryMetric: string;
  secondaryLabel: string;
  primaryTrend: string;
  secondaryTrend?: string;
  status: 'alert' | 'normal';
  confidence: number;
  chartData?: any;
  chartType?: 'line' | 'bar';
  onClick: () => void;
}

export default function KPICard({
  id,
  title,
  owners,
  horizon,
  primaryMetric,
  primaryLabel,
  secondaryMetric,
  secondaryLabel,
  primaryTrend,
  secondaryTrend,
  status,
  confidence,
  chartData,
  chartType = 'line',
  onClick,
}: KPICardProps) {
  const getMetricColor = (label: string, status: string, metricValue: string) => {
    // Specific color rules based on image description
    if (label.includes('At-Risk') || label.includes('SKUs at Risk') || label.includes('Flagged Items')) {
      return 'text-rose-500';
    }
    if (label.includes('Risk Score') || label.includes('Delay Probability')) {
      return 'text-amber-500';
    }
    if (label.includes('Optimal Price') || label.includes('Revenue Lift') || label.includes('Avg CLV') || label.includes('Q1 Forecast') || label.includes('Accuracy')) {
      return 'text-emerald-500';
    }
    if (label.includes('Current CVR') || label.includes('High-Value')) {
      return 'text-emerald-500';
    }
    if (label.includes('Decay Rate') && metricValue.includes('-')) {
      return 'text-emerald-500'; // Negative decay shown in green in image
    }
    if (label.includes('At-Risk Subs')) {
      return 'text-rose-500';
    }
    if (label.includes('Impact') || label.includes('emergency')) {
      return 'text-rose-500';
    }
    return 'text-zinc-400';
  };

  const getTrendColor = (trend: string) => {
    if (trend.includes('↑')) return 'text-emerald-500';
    if (trend.includes('↓')) return 'text-rose-500';
    return 'text-zinc-400';
  };

  return (
    <div
      onClick={onClick}
      className="relative rounded-2xl p-6 border cursor-pointer transition-all group overflow-hidden flex flex-col h-full"
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: 'var(--border-color)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'var(--bg-card)';
      }}
    >
      {/* Alert highlight strip at top */}
      {status === 'alert' && (
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 via-amber-500 to-rose-500" />
      )}

      {/* Header */}
      <div className="flex items-start justify-between mb-4 flex-shrink-0">
        <div className="flex-1">
          <div className="text-xs font-bold mb-1 font-mono" style={{ color: 'var(--accent-teal)' }}>
            KPI #{id}
          </div>
          <h3 className="text-base font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
            {title}
          </h3>
          <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--text-secondary)' }}>
            <span>{owners.join(' / ')}</span>
          </div>
        </div>
        <div
          className="px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap"
          style={{
            backgroundColor: 'rgba(139, 92, 246, 0.2)',
            color: 'var(--accent-violet)',
          }}
        >
          {horizon}
        </div>
      </div>

      {/* Metrics */}
      <div className="flex gap-6 mb-4 flex-shrink-0">
        <div className="flex-1">
          <div className="text-xs uppercase tracking-wide mb-1" style={{ color: 'var(--text-muted)' }}>
            {primaryLabel}
          </div>
          <div className={`text-2xl font-bold font-mono ${getMetricColor(primaryLabel, status, primaryMetric)}`}>
            {primaryMetric}
          </div>
          <div className={`text-xs mt-1 ${getTrendColor(primaryTrend)}`}>{primaryTrend}</div>
        </div>
        <div className="flex-1">
          <div className="text-xs uppercase tracking-wide mb-1" style={{ color: 'var(--text-muted)' }}>
            {secondaryLabel}
          </div>
          <div className={`text-2xl font-bold font-mono ${getMetricColor(secondaryLabel, status, secondaryMetric)}`}>
            {secondaryMetric}
          </div>
          {secondaryTrend && (
            <div className={`text-xs mt-1 ${getTrendColor(secondaryTrend)}`}>{secondaryTrend}</div>
          )}
        </div>
      </div>

      {/* Mini Chart */}
      {chartData && (
        <div className="h-20 mb-4 -mx-2 flex-shrink-0">
          {chartType === 'bar' ? (
            <Bar
              data={chartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false },
                  tooltip: { enabled: false },
                },
                scales: {
                  x: { display: false, grid: { display: false } },
                  y: { display: false, grid: { display: false } },
                },
                elements: {
                  bar: {
                    borderRadius: 4,
                  },
                },
              }}
            />
          ) : (
            <Line
              data={chartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false },
                  tooltip: { enabled: false },
                },
                scales: {
                  x: { display: false, grid: { display: false } },
                  y: { display: false, grid: { display: false } },
                },
                elements: {
                  point: { radius: 0 },
                  line: { 
                    tension: 0.4, 
                    borderWidth: 2,
                  },
                },
              }}
            />
          )}
        </div>
      )}

      {/* Footer with confidence and button - fixed height */}
      <div
        className="flex items-center justify-between pt-4 border-t mt-auto"
        style={{
          borderColor: 'var(--border-color)',
          minHeight: '48px',
        }}
      >
        <div className="flex items-center gap-2">
          <div
            className="w-16 h-1.5 rounded-full overflow-hidden"
            style={{ backgroundColor: 'var(--bg-secondary)' }}
          >
            <div
              className="h-full transition-all"
              style={{
                width: `${confidence}%`,
                backgroundColor: 'var(--accent-teal)',
              }}
            />
          </div>
          <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            {confidence}% confidence
          </span>
        </div>
        <button
          className="px-4 py-2 text-xs font-semibold rounded-lg transition-colors"
          style={{
            color: 'var(--text-secondary)',
            border: '1px solid var(--border-color)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'var(--accent-teal)';
            e.currentTarget.style.borderColor = 'var(--accent-teal)';
            e.currentTarget.style.color = '#ffffff';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.color = 'var(--text-secondary)';
          }}
          onClick={(e) => {
            e.stopPropagation();
            onClick();
          }}
        >
          View Details
        </button>
      </div>
    </div>
  );
}

