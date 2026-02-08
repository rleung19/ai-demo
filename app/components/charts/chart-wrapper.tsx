'use client';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

export type ChartType = 'line' | 'bar' | 'area';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

/** Chart text uses same color as "Data Sources" (--text-secondary) for consistency. */
function getThemeTextColor(): string {
  if (typeof document === 'undefined') return '#94a3b8';
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue('--text-secondary')
    .trim();
  return value || '#94a3b8';
}

/** Resolve theme muted color for grid lines. */
function getThemeGridColor(): string {
  if (typeof document === 'undefined') return 'rgba(148, 163, 184, 0.15)';
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue('--text-muted')
    .trim();
  if (!value) return 'rgba(148, 163, 184, 0.15)';
  // Convert hex to rgba with opacity for grid
  if (value.startsWith('#')) {
    const hex = value.slice(1);
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, 0.2)`;
  }
  return 'rgba(148, 163, 184, 0.15)';
}

/** Apply theme-aware colors to chart options so labels/ticks are visible in dark and light mode. */
function applyThemeColors(options: any, textColor: string, gridColor: string): any {
  const out = { ...options };
  if (out.plugins?.legend?.labels) {
    out.plugins = { ...out.plugins };
    out.plugins.legend = { ...out.plugins.legend };
    const existingLabels = out.plugins.legend.labels;
    const existingGenerateLabels = existingLabels.generateLabels;
    out.plugins.legend.labels = {
      ...existingLabels,
      color: textColor,
      generateLabels: existingGenerateLabels
        ? (chart: any) => {
            const labels = existingGenerateLabels.call(chart, chart);
            return Array.isArray(labels)
              ? labels.map((item: any) => ({ ...item, fontColor: textColor }))
              : labels;
          }
        : undefined,
    };
  }
  if (out.scales) {
    out.scales = { ...out.scales };
    for (const scaleId of Object.keys(out.scales)) {
      const scale = out.scales[scaleId];
      if (scale && typeof scale === 'object') {
        out.scales[scaleId] = {
          ...scale,
          ticks: { ...scale.ticks, color: textColor },
          title: scale.title
            ? { ...scale.title, color: textColor }
            : undefined,
          grid: scale.grid ? { ...scale.grid, color: gridColor } : undefined,
        };
      }
    }
  }
  return out;
}

interface ChartWrapperProps {
  type: ChartType;
  data: any;
  options?: any;
  height?: number;
}

export default function ChartWrapper({ type, data, options, height = 300 }: ChartWrapperProps) {
  const textColor = getThemeTextColor();
  const gridColor = getThemeGridColor();

  const defaultOptions = applyThemeColors(
    {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top' as const,
          labels: {
            color: textColor,
          },
        },
        tooltip: {
          enabled: true,
        },
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: textColor },
        },
        y: {
          grid: { color: gridColor },
          ticks: { color: textColor },
        },
      },
      ...options,
    },
    textColor,
    gridColor
  );

  // For area charts, use Line with fill option
  const chartData =
    type === 'area'
      ? {
          ...data,
          datasets: data.datasets.map((dataset: any) => ({
            ...dataset,
            fill: true,
          })),
        }
      : data;

  // For horizontal bar charts, set indexAxis
  const barOptions =
    type === 'bar' && options?.indexAxis === 'y'
      ? { ...defaultOptions, indexAxis: 'y' as const }
      : defaultOptions;

  return (
    <div style={{ height: `${height}px` }}>
      {type === 'bar' ? (
        <Bar data={chartData} options={barOptions} />
      ) : (
        <Line data={chartData} options={defaultOptions} />
      )}
    </div>
  );
}

