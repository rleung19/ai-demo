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

interface ChartWrapperProps {
  type: ChartType;
  data: any;
  options?: any;
  height?: number;
}

export default function ChartWrapper({ type, data, options, height = 300 }: ChartWrapperProps) {
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: 'rgb(113, 113, 122)', // zinc-500
        },
      },
      tooltip: {
        enabled: true,
      },
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(161, 161, 170, 0.1)', // zinc-300 with opacity
        },
        ticks: {
          color: 'rgb(113, 113, 122)', // zinc-500
        },
      },
      y: {
        grid: {
          color: 'rgba(161, 161, 170, 0.1)', // zinc-300 with opacity
        },
        ticks: {
          color: 'rgb(113, 113, 122)', // zinc-500
        },
      },
    },
    ...options,
  };

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

