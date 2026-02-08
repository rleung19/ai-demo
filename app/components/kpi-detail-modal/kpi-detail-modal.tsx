'use client';

import { useEffect, useState } from 'react';
import { KPIDetailData } from '@/app/lib/types/kpi';
import ChartWrapper from '../charts/chart-wrapper';
import {
  getVipTopAtRiskCustomers,
  triggerVipAgenticFlow,
  VipAgenticFlowResult,
  VipCohortUser,
} from '@/app/lib/api/churn-api';

// Cohort definitions for tooltips
const cohortDefinitions: Record<string, string> = {
  VIP: 'High-value customers with lifetime value over $5,000 or loyalty card membership. These are premium customers who represent significant revenue.',
  Regular: 'Active customers who have made at least 2 purchases, are active within the last 90 days, and regularly log in. These are engaged, stable customers.',
  New: 'Recently acquired customers who have been members for less than 1 year. These customers are still in the onboarding phase.',
  Dormant: 'Inactive customers who have not made a purchase in over 90 days or have not logged in. These customers are at high risk of churn.',
  Other: 'Customers who do not fit into the other defined segments.',
};

// Impact score definition
const impactScoreDefinition = 'Impact Score represents the average churn probability (0-100%) for customers affected by this risk factor. A higher score means customers with this factor have a higher likelihood of churning.';

interface KPIDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  kpiData: KPIDetailData | null;
}

export default function KPIDetailModal({ isOpen, onClose, kpiData }: KPIDetailModalProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  const [vipFlowLoading, setVipFlowLoading] = useState(false);
  const [vipFlowStatus, setVipFlowStatus] = useState<'idle' | 'success' | 'error' | 'info'>(
    'idle'
  );
  const [vipFlowMessage, setVipFlowMessage] = useState<string | null>(null);
  const [vipFlowProcessed, setVipFlowProcessed] = useState<number | null>(null);

  const vipWebhookUrl = process.env.NEXT_PUBLIC_AGENTIC_FLOW_WEBHOOK_URL;
  const isVipAgenticEnabled = !!vipWebhookUrl;

  if (!isOpen) return null;

  // Show loading state if data is not available
  if (!kpiData) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm bg-black/50">
        <div
          className="rounded-2xl p-8 border max-w-md w-full"
          style={{
            backgroundColor: 'var(--bg-card)',
            borderColor: 'var(--border-color)',
          }}
        >
          <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: 'var(--accent-teal)' }}></div>
            <p style={{ color: 'var(--text-secondary)' }}>Loading KPI data...</p>
          </div>
        </div>
      </div>
    );
  }

  const { metadata, metrics, actions, impact, alert, cohorts, insight, chartData, chartOptions } =
    kpiData;

  // Determine chart type based on KPI ID
  const getChartType = () => {
    if (metadata.id === 1) return 'bar'; // Churn - stacked bar
    if (metadata.id === 2) return 'bar'; // Stockout - horizontal bar
    if (metadata.id === 3) return 'line'; // Price elasticity - line with dual axis
    if (metadata.id === 4) return 'bar'; // CAC - bar
    if (metadata.id === 5) return 'bar'; // Return rate - grouped bar
    if (metadata.id === 6) return 'line'; // Email decay - line
    if (metadata.id === 7) return 'bar'; // Supply chain - horizontal bar
    if (metadata.id === 8) return 'line'; // Conversion - line with bands
    if (metadata.id === 9) return 'bar'; // CLV - bar
    if (metadata.id === 10) return 'line'; // Demand forecast - line with confidence bands
    return 'line';
  };

  const handleVipProceed = async () => {
    if (!metadata || metadata.id !== 1) return;
    if (!isVipAgenticEnabled) return;

    const confirmed = window.confirm('Proceed to launch VIP re-engagement campaign?');
    if (!confirmed) {
      return;
    }

    setVipFlowLoading(true);
    setVipFlowStatus('idle');
    setVipFlowMessage(null);
    setVipFlowProcessed(null);

    try {
      const users: VipCohortUser[] = await getVipTopAtRiskCustomers();

      if (!users || users.length === 0) {
        setVipFlowStatus('info');
        setVipFlowMessage('No at-risk VIP customers to re-engage at this time.');
        return;
      }

      const result: VipAgenticFlowResult = await triggerVipAgenticFlow(users);

      if (result.success) {
        setVipFlowStatus('success');
      } else {
        setVipFlowStatus('error');
      }
      setVipFlowMessage(result.message);
      if (typeof result.processed === 'number') {
        setVipFlowProcessed(result.processed);
      }
    } catch (error: any) {
      console.error('[KPIDetailModal] VIP agentic flow failed:', error);
      setVipFlowStatus('error');
      setVipFlowMessage(
        error?.message || 'VIP re-engagement flow failed: unable to contact API or webhook.'
      );
    } finally {
      setVipFlowLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.7)' }}
      onClick={onClose}
    >
      <div
        className="rounded-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden shadow-2xl"
        style={{
          backgroundColor: 'var(--bg-secondary)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Sticky Header */}
        <div
          className="sticky top-0 z-10 px-6 py-4 border-b"
          style={{
            backgroundColor: 'var(--bg-secondary)',
            borderColor: 'var(--border-color)',
          }}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <span
                  className="px-3 py-1 text-xs font-bold rounded-full font-mono"
                  style={{
                    color: 'var(--accent-teal)',
                    backgroundColor: 'rgba(20, 184, 166, 0.2)',
                  }}
                >
                  KPI #{metadata.id}
                </span>
                <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                  {metadata.title}
                </h2>
              </div>
              <p className="text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
                {metadata.predictionHorizon} horizon • {metadata.owners.join(' / ')}
              </p>
              <div className="flex items-center gap-2 flex-wrap">
                {metadata.owners.map((owner) => (
                  <span
                    key={owner}
                    className="px-2 py-1 text-xs font-semibold rounded"
                    style={{
                      backgroundColor: 'rgba(139, 92, 246, 0.2)',
                      color: 'var(--accent-violet)',
                    }}
                  >
                    {owner}
                  </span>
                ))}
                <span
                  className="px-2 py-1 text-xs font-semibold rounded"
                  style={{
                    backgroundColor: 'rgba(139, 92, 246, 0.2)',
                    color: 'var(--accent-violet)',
                  }}
                >
                  {metadata.predictionHorizon}
                </span>
                {metadata.note && (
                  <span
                    className="px-2 py-1 text-xs font-semibold rounded flex items-center gap-1"
                    style={{
                      backgroundColor: 'rgba(245, 158, 11, 0.2)',
                      color: '#f59e0b',
                    }}
                    title={metadata.note}
                  >
                    ⚠️ {metadata.note}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="ml-4 p-2 rounded-lg transition-colors"
              style={{
                color: 'var(--text-secondary)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)';
                e.currentTarget.style.color = 'var(--text-primary)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = 'var(--text-secondary)';
              }}
              aria-label="Close modal"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Scrollable Body */}
        <div className="overflow-y-auto max-h-[calc(90vh-120px)] px-6 py-6">
          {/* Alert Banner */}
          {alert && (
            <div
              className="rounded-xl p-4 mb-6 flex items-start gap-4"
              style={{
                background: 'linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(244, 63, 94, 0.15) 100%)',
                border: '1px solid rgba(249, 115, 22, 0.3)',
              }}
            >
              <div className="text-2xl">{alert.icon}</div>
              <div className="flex-1">
                <h5 className="font-semibold mb-1" style={{ color: '#f59e0b' }}>
                  {alert.title}
                </h5>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  {alert.description}
                </p>
              </div>
            </div>
          )}

          {/* Key Metrics Grid */}
          <div className="mb-6">
            <h3 className="text-sm uppercase font-semibold mb-4 tracking-wide" style={{ color: 'var(--text-muted)' }}>
              Key Metrics
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {metrics.map((metric, idx) => (
                <div
                  key={idx}
                  className="rounded-xl p-5 border text-center"
                  style={{
                    backgroundColor: 'var(--bg-card)',
                    borderColor: 'var(--border-color)',
                  }}
                >
                  <div className="text-xs uppercase tracking-wide mb-2" style={{ color: 'var(--text-muted)' }}>
                    {metric.label}
                  </div>
                  <div
                    className={`text-3xl font-bold font-mono mb-1 ${
                      metric.color === 'emerald'
                        ? 'text-emerald-500'
                        : metric.color === 'amber'
                          ? 'text-amber-500'
                          : metric.color === 'rose'
                            ? 'text-rose-500'
                            : metric.color === 'teal'
                              ? 'text-teal-500'
                              : 'text-blue-500'
                    }`}
                  >
                    {metric.value}
                  </div>
                  {metric.trendValue && (
                    <div
                      className="text-xs"
                      style={{
                        color:
                          metric.trend === 'up'
                            ? '#10b981'
                            : metric.trend === 'down'
                              ? '#f43f5e'
                              : 'var(--text-muted)',
                      }}
                    >
                      {metric.trendValue}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Main Visualization Chart */}
          {chartData && (
            <div className="mb-6">
              <h3 className="text-sm uppercase font-semibold mb-4 tracking-wide" style={{ color: 'var(--text-muted)' }}>
                Main Visualization
              </h3>
              <div
                className="rounded-xl p-6 border"
                style={{
                  backgroundColor: 'var(--bg-card)',
                  borderColor: 'var(--border-color)',
                }}
              >
                <ChartWrapper
                  type={getChartType()}
                  data={chartData}
                  options={chartOptions}
                  height={300}
                />
              </div>
            </div>
          )}

          {/* Cohort Grid */}
          {cohorts && cohorts.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm uppercase font-semibold mb-4 tracking-wide" style={{ color: 'var(--text-muted)' }}>
                Segment Breakdown
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {cohorts.map((cohort, idx) => {
                  // Extract base cohort name (remove " Customers" suffix if present)
                  const baseCohortName = cohort.name.replace(' Customers', '').trim();
                  const definition = cohortDefinitions[baseCohortName] || cohortDefinitions[cohort.name] || 'Customer segment definition not available.';
                  return (
                    <div
                      key={idx}
                      className="rounded-xl p-5 border relative group cursor-help"
                      style={{
                        backgroundColor: 'var(--bg-card)',
                        borderColor:
                          cohort.riskLevel === 'high'
                            ? 'rgba(244, 63, 94, 0.3)'
                            : cohort.riskLevel === 'medium'
                              ? 'rgba(245, 158, 11, 0.3)'
                              : 'rgba(16, 185, 129, 0.3)',
                      }}
                      title={definition}
                    >
                      <div className="text-xs mb-2 flex items-center gap-1" style={{ color: 'var(--text-muted)' }}>
                        {cohort.name}
                        <span className="text-[10px] opacity-60" title={definition}>ℹ️</span>
                      </div>
                    <div
                      className="text-2xl font-bold font-mono mb-1"
                      style={{
                        color:
                          cohort.riskLevel === 'high'
                            ? '#f43f5e'
                            : cohort.riskLevel === 'medium'
                              ? '#f59e0b'
                              : '#10b981',
                      }}
                    >
                      {cohort.value}
                    </div>
                    <div 
                      className="text-xs whitespace-pre-line" 
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      {cohort.label}
                    </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Top Churn Risk Factors Table */}
          {kpiData.tableData && kpiData.tableData.length > 0 && metadata.id === 1 && (
            <div className="mb-6">
              <h3 className="text-sm uppercase font-semibold mb-4 tracking-wide" style={{ color: 'var(--text-secondary)' }}>
                Top Churn Risk Factors
              </h3>
              <div
                className="overflow-x-auto rounded-xl border"
                style={{
                  backgroundColor: 'var(--bg-card)',
                  borderColor: 'var(--border-color)',
                }}
              >
                <table className="w-full text-sm">
                  <thead style={{ backgroundColor: 'var(--bg-secondary)' }}>
                    <tr>
                      <th
                        className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                        style={{ color: 'var(--text-secondary)' }}
                      >
                        RISK FACTOR
                      </th>
                      <th
                        className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide cursor-help relative group"
                        style={{ color: 'var(--text-secondary)' }}
                        title={impactScoreDefinition}
                      >
                        <div className="flex items-center gap-1">
                          IMPACT SCORE
                          <span className="text-[10px] opacity-60" title={impactScoreDefinition}>ℹ️</span>
                        </div>
                      </th>
                      <th
                        className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                        style={{ color: 'var(--text-secondary)' }}
                      >
                        AFFECTED CUSTOMERS
                      </th>
                      <th
                        className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                        style={{ color: 'var(--text-secondary)' }}
                      >
                        PRIMARY SEGMENT
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {kpiData.tableData.map((row: any, idx: number) => {
                      // Parse impact score to determine color
                      const impactScore = parseFloat(String(row.impactScore || row.impact_score || '0').replace('%', ''));
                      let impactColor = '#10b981'; // green (low)
                      if (impactScore >= 70) {
                        impactColor = '#f43f5e'; // red (high)
                      } else if (impactScore >= 50) {
                        impactColor = '#f59e0b'; // orange (medium)
                      }

                      return (
                        <tr
                          key={idx}
                          className="border-t transition-colors"
                          style={{
                            borderColor: 'var(--border-color)',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = 'transparent';
                          }}
                        >
                          <td className="px-4 py-3" style={{ color: 'var(--text-secondary)' }}>
                            {row.riskFactor || row.risk_factor || 'N/A'}
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <div
                                className="w-2 h-2 rounded-full"
                                style={{ backgroundColor: impactColor }}
                              />
                              <span style={{ color: 'var(--text-secondary)' }}>
                                {row.impactScore || row.impact_score || 'N/A'}
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-3" style={{ color: 'var(--text-secondary)' }}>
                            {typeof row.affectedCustomers === 'number'
                              ? row.affectedCustomers.toLocaleString()
                              : row.affectedCustomers || row.affected_customers || 'N/A'}
                          </td>
                          <td className="px-4 py-3" style={{ color: 'var(--text-secondary)' }}>
                            {row.primarySegment || row.primary_segment || 'N/A'}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Insight Box */}
          {insight && (
            <div
              className="mb-6 rounded-xl p-5 border"
              style={{
                backgroundColor:
                  insight.type === 'success'
                    ? 'rgba(16, 185, 129, 0.1)'
                    : insight.type === 'warning'
                      ? 'rgba(245, 158, 11, 0.1)'
                      : 'rgba(59, 130, 246, 0.1)',
                borderColor:
                  insight.type === 'success'
                    ? 'rgba(16, 185, 129, 0.3)'
                    : insight.type === 'warning'
                      ? 'rgba(245, 158, 11, 0.3)'
                      : 'rgba(59, 130, 246, 0.3)',
              }}
            >
              <h5
                className="font-semibold mb-2"
                style={{
                  color:
                    insight.type === 'success'
                      ? '#10b981'
                      : insight.type === 'warning'
                        ? '#f59e0b'
                        : '#3b82f6',
                }}
              >
                {insight.title}
              </h5>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                {insight.content}
              </p>
            </div>
          )}

          {/* AI Model Information */}
          <div
            className="rounded-xl p-6 mb-6 border"
            style={{
              backgroundColor: 'var(--bg-card)',
              borderColor: 'var(--border-color)',
            }}
          >
            <h3 className="text-sm uppercase font-semibold mb-4 tracking-wide" style={{ color: 'var(--text-muted)' }}>
              AI Model Information
            </h3>
            <div className="space-y-3 text-sm">
              <div>
                <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Model Type:
                </span>
                <span className="ml-2" style={{ color: 'var(--text-secondary)' }}>
                  {metadata.modelType}
                </span>
              </div>
              <div>
                <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Training Data:
                </span>
                <span className="ml-2" style={{ color: 'var(--text-secondary)' }}>
                  {metadata.trainingData}
                </span>
              </div>
              <div>
                <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Confidence Level:
                </span>
                <span className="ml-2" style={{ color: 'var(--text-secondary)' }}>
                  {metadata.confidence}%
                </span>
              </div>
              <div>
                <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Last Update:
                </span>
                <span className="ml-2" style={{ color: 'var(--text-secondary)' }}>
                  {metadata.lastUpdate}
                </span>
              </div>
              <div>
                <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Data Sources:
                </span>
                <span className="ml-2" style={{ color: 'var(--text-secondary)' }}>
                  {metadata.dataSources.join(', ')}
                </span>
              </div>
            </div>
          </div>

          {/* Recommended Actions */}
          <div className="mb-6">
            <h3 className="text-sm uppercase font-semibold mb-4 tracking-wide" style={{ color: 'var(--text-muted)' }}>
              AI-Recommended Actions
            </h3>
            {metadata.id === 1 && vipFlowStatus !== 'idle' && vipFlowMessage && (
              <div
                className="mb-4 rounded-lg p-4 text-sm"
                style={{
                  backgroundColor:
                    vipFlowStatus === 'success'
                      ? 'rgba(16, 185, 129, 0.1)'
                      : vipFlowStatus === 'error'
                        ? 'rgba(244, 63, 94, 0.1)'
                        : 'rgba(59, 130, 246, 0.1)',
                  border: '1px solid',
                  borderColor:
                    vipFlowStatus === 'success'
                      ? 'rgba(16, 185, 129, 0.4)'
                      : vipFlowStatus === 'error'
                        ? 'rgba(244, 63, 94, 0.4)'
                        : 'rgba(59, 130, 246, 0.4)',
                  color:
                    vipFlowStatus === 'success'
                      ? '#10b981'
                      : vipFlowStatus === 'error'
                        ? '#f43f5e'
                        : '#3b82f6',
                }}
              >
                <div className="flex items-center justify-between gap-2">
                  <div>
                    <div className="font-semibold mb-1">
                      {vipFlowStatus === 'success'
                        ? 'VIP re-engagement triggered'
                        : vipFlowStatus === 'error'
                          ? 'VIP re-engagement failed'
                          : 'No at-risk VIP customers'}
                    </div>
                    <div>
                      {vipFlowMessage}
                      {typeof vipFlowProcessed === 'number' && vipFlowProcessed >= 0 && (
                        <span>{` (Processed ${vipFlowProcessed} VIP customers)`}</span>
                      )}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setVipFlowStatus('idle');
                      setVipFlowMessage(null);
                      setVipFlowProcessed(null);
                    }}
                    className="text-xs px-2 py-1 rounded border"
                    style={{
                      borderColor: 'var(--border-color)',
                      color: 'var(--text-secondary)',
                    }}
                    aria-label="Dismiss VIP re-engagement status"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            )}
            <div className="space-y-4">
              {actions.map((action) => {
                const isVipAgenticCard =
                  metadata.id === 1 && action.id === '1' && isVipAgenticEnabled;
                const isOtherAction = metadata.id === 1 && action.id !== '1';
                
                const handleFakeProceed = () => {
                  window.alert(`"Proceed" functionality for "${action.title}" is coming soon.`);
                };
                
                return (
                  <div
                    key={action.id}
                    className="p-5 rounded-xl border-l-4"
                    style={{
                      borderLeftColor:
                        action.priority === 'high'
                          ? '#f43f5e'
                          : action.priority === 'medium'
                            ? '#f59e0b'
                            : '#14b8a6',
                      backgroundColor:
                        action.priority === 'high'
                          ? 'rgba(244, 63, 94, 0.1)'
                          : action.priority === 'medium'
                            ? 'rgba(245, 158, 11, 0.1)'
                            : 'rgba(20, 184, 166, 0.1)',
                    }}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {action.title}
                      </h4>
                      <span
                        className="px-2 py-1 text-xs font-semibold rounded"
                        style={{
                          backgroundColor:
                            action.priority === 'high'
                              ? 'rgba(244, 63, 94, 0.2)'
                              : action.priority === 'medium'
                                ? 'rgba(245, 158, 11, 0.2)'
                                : 'rgba(20, 184, 166, 0.2)',
                          color:
                            action.priority === 'high'
                              ? '#f43f5e'
                              : action.priority === 'medium'
                                ? '#f59e0b'
                                : '#14b8a6',
                        }}
                      >
                        {action.priority.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>
                      {action.description}
                    </p>
                    <div className="flex flex-wrap gap-2 text-xs items-center justify-between">
                      <div className="flex flex-wrap gap-2">
                        <span
                          className="px-3 py-1 rounded"
                          style={{
                            backgroundColor: 'rgba(139, 92, 246, 0.2)',
                            color: 'var(--accent-violet)',
                          }}
                        >
                          {action.owner}
                        </span>
                        <span
                          className="px-3 py-1 rounded"
                          style={{
                            backgroundColor: 'rgba(59, 130, 246, 0.2)',
                            color: '#3b82f6',
                          }}
                        >
                          Due: {action.dueDate}
                        </span>
                        {action.impact && (
                          <span
                            className="px-3 py-1 rounded"
                            style={{
                              backgroundColor: 'rgba(16, 185, 129, 0.2)',
                              color: '#10b981',
                            }}
                          >
                            {action.impact}
                          </span>
                        )}
                      </div>
                      {(isVipAgenticCard || isOtherAction) && (
                        <button
                          type="button"
                          onClick={isVipAgenticCard ? handleVipProceed : handleFakeProceed}
                          disabled={isVipAgenticCard && vipFlowLoading}
                          className="mt-3 md:mt-0 px-4 py-2 rounded-lg text-sm font-semibold shadow-sm transition-colors"
                          style={{
                            backgroundColor: isVipAgenticCard && vipFlowLoading 
                              ? 'rgba(15, 118, 110, 0.6)' 
                              : isVipAgenticCard 
                                ? '#0f766e'
                                : '#6b7280',
                            color: '#ecfeff',
                            opacity: (isVipAgenticCard && vipFlowLoading) ? 0.8 : 1,
                          }}
                          aria-label={
                            isVipAgenticCard 
                              ? 'Proceed with VIP re-engagement campaign'
                              : `Proceed with ${action.title}`
                          }
                        >
                          {isVipAgenticCard && vipFlowLoading ? 'Processing…' : 'Proceed'}
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Business Impact Summary */}
          {impact && (
            <div
              className="rounded-xl p-6 border"
              style={{
                background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)',
                borderColor: 'rgba(139, 92, 246, 0.3)',
              }}
            >
              <h3 className="text-sm uppercase font-semibold mb-4 tracking-wide" style={{ color: 'var(--accent-violet)' }}>
                Business Impact Summary
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-xs mb-1" style={{ color: 'var(--text-muted)' }}>
                    Revenue Impact
                  </div>
                  <div className="text-2xl font-bold font-mono" style={{ color: 'var(--text-primary)' }}>
                    ${Math.abs(impact.revenueImpact / 1000).toFixed(0)}K
                  </div>
                </div>
                <div>
                  <div className="text-xs mb-1" style={{ color: 'var(--text-muted)' }}>
                    Cost Impact
                  </div>
                  <div className="text-2xl font-bold font-mono" style={{ color: 'var(--text-primary)' }}>
                    ${Math.abs(impact.costImpact / 1000).toFixed(0)}K
                  </div>
                </div>
                {impact.roi !== undefined && (
                  <div>
                    <div className="text-xs mb-1" style={{ color: 'var(--text-muted)' }}>
                      ROI
                    </div>
                    <div className="text-2xl font-bold font-mono" style={{ color: '#10b981' }}>
                      {impact.roi > 0 ? '+' : ''}
                      {impact.roi.toFixed(0)}%
                    </div>
                  </div>
                )}
              </div>
              {impact.description && (
                <div className="mt-4 text-sm" style={{ color: 'var(--text-secondary)' }}>
                  {impact.description}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
