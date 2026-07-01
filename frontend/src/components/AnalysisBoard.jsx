import React, { useState } from 'react';
import FixPanel from './FixPanel';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export default function AnalysisBoard({ analysis, isAnalyzing, originalCode, code }) {
  const [showFix, setShowFix] = useState(false);
  const [exportingReport, setExportingReport] = useState(false);

  const handleExportReport = async () => {
    if (!analysis) return;
    setExportingReport(true);
    try {
      const res = await fetch(`${API}/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis_result: analysis, code: code || originalCode || '' }),
      });
      const data = await res.json();
      if (!res.ok || data.error) throw new Error(data.error || 'Report generation failed');

      // Trigger browser download
      const blob = new Blob([data.report], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'astra_report.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      alert(e.message || 'Failed to generate report');
    } finally {
      setExportingReport(false);
    }
  };

  if (isAnalyzing) {
    return (
      <div className="analysis-board flex-center">
        <div className="loading-text">
          Analyzing code structure...
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="analysis-board empty-state">
        Enter code and click Analyze to see results here.
      </div>
    );
  }

  const hasFunctions = Array.isArray(analysis.functions) && analysis.functions.length > 0;

  return (
    <div className="analysis-board">
      <div className="board-header">
        Analysis Results
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button
            id="export-report-btn"
            className="fix-btn"
            onClick={handleExportReport}
            disabled={exportingReport}
            title="Download plain-text analysis report"
            style={{ opacity: exportingReport ? 0.6 : 1 }}
          >
            {exportingReport ? '⏳ Exporting…' : '📄 Export Report'}
          </button>
          <button
            className="fix-btn"
            onClick={() => setShowFix(true)}
            title="Let AI rewrite the code to fix detected issues"
          >
            ⚡ Fix My Code
          </button>
        </div>
      </div>

      <div className="board-content">
        <div className="score-section" style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <label className="section-label-block">Quality Score</label>
          <div className="score-circle" style={{ margin: '0.5rem auto 0' }}>
            {analysis.quality_score}
          </div>
        </div>

        <div className="metrics-grid">
          <div className="metric-card">
            <label>Time Complexity</label>
            <span>{analysis.analysis.time_complexity}</span>
          </div>
          <div className="metric-card">
            <label>Space Complexity</label>
            <span>{analysis.analysis.space_complexity}</span>
          </div>
        </div>

        <div className="mt-1">
          <label className="section-label">Patterns Detected</label>
          <div className="patterns-list">
            {analysis.patterns.map((p, i) => (
              <span key={i} className="pattern-badge">{p.replace('_', ' ')}</span>
            ))}
            {analysis.patterns.length === 0 && <span className="clean-code-badge">Clean code!</span>}
          </div>
        </div>

        <div className="insight-section">
          <label className="section-label-block">AI Insights</label>
          <div className="insight-card">
            <span className={`font-semibold ${analysis.ai.prediction.label === 'Efficient' ? 'text-success' : 'text-warning'}`}>
              {analysis.ai.prediction.label}
            </span>
            <span className="confidence-text">
              ({(analysis.ai.prediction.confidence * 100).toFixed(1)}% confidence)
            </span>
            <p className="mt-05">{analysis.explanation}</p>
          </div>
        </div>

        {/* SECTION C — Dead Code */}
        {analysis.analysis.dead_code?.length > 0 && (
          <div className="insight-section mt-1">
            <label className="section-label-block">💀 Dead Code Detected</label>
            <div className="mb-1" style={{ fontSize: '0.9em', opacity: 0.8 }}>
              {analysis.analysis.dead_code.length} issues found
            </div>
            {analysis.analysis.dead_code.map((item, i) => (
              <div key={i} className="insight-card mb-05" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="pattern-badge" style={{
                  backgroundColor: item.severity === 'high' ? 'var(--danger)' : item.severity === 'medium' ? 'var(--warning-color)' : 'var(--warning)',
                  color: '#fff'
                }}>
                  {item.severity}
                </span>
                <span style={{ fontWeight: 'bold' }}>{item.pattern.replace(/_/g, ' ')}</span>
                <span style={{ opacity: 0.8 }}>— {item.message}</span>
              </div>
            ))}
          </div>
        )}

        {/* SECTION D — Halstead Metrics */}
        {analysis.analysis.halstead && Object.keys(analysis.analysis.halstead).length > 0 && (
          <div className="insight-section mt-1">
            <label className="section-label-block">📐 Halstead Complexity</label>
            <div className="metrics-grid mt-1">
              <div className="metric-card">
                <label>Volume</label>
                <span>{Math.round(analysis.analysis.halstead.volume)}</span>
                <div style={{ fontSize: '0.8em', opacity: 0.8 }}>{analysis.analysis.halstead.volume_label}</div>
              </div>
              <div className="metric-card">
                <label>Difficulty</label>
                <span>{analysis.analysis.halstead.difficulty.toFixed(1)}</span>
                <div style={{ fontSize: '0.8em', opacity: 0.8 }}>{analysis.analysis.halstead.difficulty_label}</div>
              </div>
              <div className="metric-card">
                <label>Bugs Estimated</label>
                <span style={{
                  color: analysis.analysis.halstead.bugs_estimated < 0.05 ? 'var(--success)' :
                         analysis.analysis.halstead.bugs_estimated <= 0.2 ? 'var(--warning-color)' : 'var(--danger)'
                }}>
                  {analysis.analysis.halstead.bugs_estimated.toFixed(3)}
                </span>
                <div style={{ fontSize: '0.8em', opacity: 0.8 }}>{analysis.analysis.halstead.bugs_label}</div>
              </div>
            </div>
            <div className="mt-05" style={{ fontSize: '0.8em', opacity: 0.6 }}>
              Based on Halstead's 1977 software science metrics
            </div>
          </div>
        )}

        {/* SECTION E — Type Info */}
        {analysis.analysis.type_info && analysis.analysis.type_info.variables && Object.keys(analysis.analysis.type_info.variables).length > 0 && (
          <div className="insight-section mt-1">
            <label className="section-label-block">🔬 Inferred Types</label>
            <div className="fn-table-wrap mt-05">
              <table className="fn-table" style={{ fontSize: '0.9em' }}>
                <thead>
                  <tr>
                    <th>Variable</th>
                    <th>Inferred Type</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(analysis.analysis.type_info.variables).map(([v, info], i) => (
                    <tr key={i}>
                      <td className="fn-name">{v}</td>
                      <td className="fn-mono">{info.type}</td>
                      <td>{(info.confidence * 100).toFixed(0)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {analysis.analysis.type_info.parameter_hints && Object.keys(analysis.analysis.type_info.parameter_hints).length > 0 && (
              <div className="mt-1" style={{ fontSize: '0.85em', opacity: 0.8 }}>
                {Object.entries(analysis.analysis.type_info.parameter_hints).map(([p, t], i) => (
                  <div key={i}>param {p} inferred as: {t} (from usage)</div>
                ))}
              </div>
            )}
            <div className="mt-05" style={{ fontSize: '0.8em', opacity: 0.6 }}>
              Inferred statically — no execution required
            </div>
          </div>
        )}

        {analysis.analysis.cyclomatic && (
          <div className="insight-section">
            <details open style={{ cursor: 'pointer' }}>
              <summary className="section-label-block">🔀 Cyclomatic Complexity</summary>
              <div className="insight-card mt-1">
                <div style={{ textAlign: 'center' }}>
                  <div className="score-circle" style={{
                    margin: '0.5rem auto 0',
                    color: analysis.analysis.cyclomatic.risk_level === 'low' ? 'var(--success)' :
                           analysis.analysis.cyclomatic.risk_level === 'moderate' ? 'var(--warning-color)' :
                           analysis.analysis.cyclomatic.risk_level === 'high' ? 'var(--warning)' : 'var(--danger)'
                  }}>
                    {analysis.analysis.cyclomatic.score}
                  </div>
                  <div className="mt-1" style={{ fontSize: '0.9em', opacity: 0.8 }}>
                    {analysis.analysis.cyclomatic.risk_label}
                  </div>
                </div>

                {analysis.analysis.cyclomatic.per_function && analysis.analysis.cyclomatic.per_function.length > 1 && (
                  <div className="fn-table-wrap mt-1">
                    <table className="fn-table" style={{ fontSize: '0.85em' }}>
                      <thead>
                        <tr>
                          <th>Function</th>
                          <th>Score</th>
                          <th>Risk level</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analysis.analysis.cyclomatic.per_function.map((fn, i) => (
                          <tr key={i}>
                            <td className="fn-name">{fn.name}</td>
                            <td className="fn-mono">{fn.score}</td>
                            <td>
                              <span style={{
                                display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%',
                                backgroundColor: fn.risk_level === 'low' ? 'var(--success)' : fn.risk_level === 'moderate' ? 'yellow' : fn.risk_level === 'high' ? 'var(--warning)' : 'var(--danger)',
                                marginRight: '5px'
                              }}></span>
                              {fn.risk_level.replace('_', ' ')}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </details>
          </div>
        )}

        {analysis.analysis.confidence && (
          <div className="insight-section">
            <details open style={{ cursor: 'pointer' }}>
              <summary className="section-label-block">📊 Analysis Confidence</summary>
              <div className="insight-card mt-1">
                <div className="mb-1">
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9em' }}>
                    <span>Time Complexity:</span>
                    <span>{(analysis.analysis.confidence.time_confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div style={{ background: '#333', height: '8px', borderRadius: '4px', marginTop: '4px' }}>
                    <div style={{
                      height: '100%', borderRadius: '4px',
                      width: `${analysis.analysis.confidence.time_confidence * 100}%`,
                      backgroundColor: analysis.analysis.confidence.time_confidence >= 0.85 ? 'var(--success)' : analysis.analysis.confidence.time_confidence >= 0.70 ? 'yellow' : 'var(--warning)'
                    }}></div>
                  </div>
                  {analysis.analysis.confidence.time_alternative && (
                    <div style={{ fontSize: '0.8em', opacity: 0.8, marginTop: '4px' }}>
                      Alternative: {analysis.analysis.confidence.time_alternative} — {analysis.analysis.confidence.time_alt_reason}
                    </div>
                  )}
                  {analysis.analysis.confidence.time_reductions && analysis.analysis.confidence.time_reductions.length > 0 && (
                    <ul style={{ fontSize: '0.8em', opacity: 0.8, marginTop: '4px', paddingLeft: '1rem', listStyleType: 'disc' }}>
                      {analysis.analysis.confidence.time_reductions.map((r, i) => (
                        <li key={i}>{r} — confidence reduced</li>
                      ))}
                    </ul>
                  )}
                </div>

                <div style={{ marginTop: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9em' }}>
                    <span>Space Complexity:</span>
                    <span>{(analysis.analysis.confidence.space_confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div style={{ background: '#333', height: '8px', borderRadius: '4px', marginTop: '4px' }}>
                    <div style={{
                      height: '100%', borderRadius: '4px',
                      width: `${analysis.analysis.confidence.space_confidence * 100}%`,
                      backgroundColor: analysis.analysis.confidence.space_confidence >= 0.85 ? 'var(--success)' : analysis.analysis.confidence.space_confidence >= 0.70 ? 'yellow' : 'var(--warning)'
                    }}></div>
                  </div>
                </div>
              </div>
            </details>
          </div>
        )}

        {analysis.analysis.eco_metrics && (
          <div className="insight-section">
            <label className="section-label-block">🌿 Green Code / Eco-Score</label>
            <div className="insight-card">
              <div className="flex-between-mb">
                <span>
                  <strong>Rating:</strong>{' '}
                  <span className={
                    analysis.analysis.eco_metrics.eco_score_100 > 60 ? 'text-success' :
                    analysis.analysis.eco_metrics.eco_score_100 > 40 ? 'text-warning' : 'text-danger'
                  }>
                    {analysis.analysis.eco_metrics.eco_rating}
                  </span>
                  {' '}({analysis.analysis.eco_metrics.eco_score_100}/100)
                </span>
              </div>
              <div className="eco-details">
                <strong>Carbon Footprint:</strong> {analysis.analysis.eco_metrics.carbon_gco2e_1m} gCO₂e per 1M executions<br />
                <strong>Energy Usage:</strong> {analysis.analysis.eco_metrics.energy_joules_1m} Joules per 1M executions
              </div>
            </div>
          </div>
        )}

        {/* ── Per-function breakdown (Python only) ── */}
        {hasFunctions && (
          <div className="insight-section">
            <label className="section-label-block">𝑓 Function Breakdown</label>
            <div className="fn-table-wrap">
              <table className="fn-table">
                <thead>
                  <tr>
                    <th>Function</th>
                    <th>Time</th>
                    <th>Space</th>
                    <th>Score</th>
                    <th>Patterns</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.functions.map((fn, i) => (
                    <tr key={i} className={fn.quality_score < 40 ? 'fn-row-bad' : fn.quality_score < 70 ? 'fn-row-warn' : 'fn-row-ok'}>
                      <td className="fn-name">{fn.name}</td>
                      <td className="fn-mono">{fn.time_complexity}</td>
                      <td className="fn-mono">{fn.space_complexity}</td>
                      <td>
                        <span className={`fn-score ${fn.quality_score < 40 ? 'fn-score-bad' : fn.quality_score < 70 ? 'fn-score-warn' : 'fn-score-ok'}`}>
                          {fn.quality_score}
                        </span>
                      </td>
                      <td className="fn-patterns">
                        {fn.patterns.length > 0
                          ? fn.patterns.map((p, j) => (
                              <span key={j} className="pattern-badge fn-pattern-badge">{p.replace('_', ' ')}</span>
                            ))
                          : <span className="clean-code-badge">✓ clean</span>
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {showFix && (
        <FixPanel
          originalCode={originalCode}
          analysis={analysis}
          onClose={() => setShowFix(false)}
        />
      )}
    </div>
  );
}
