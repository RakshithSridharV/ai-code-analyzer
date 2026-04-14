import React, { useState } from 'react';
import FixPanel from './FixPanel';

export default function AnalysisBoard({ analysis, isAnalyzing, originalCode }) {
  const [showFix, setShowFix] = useState(false);

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
        <button
          className="fix-btn"
          onClick={() => setShowFix(true)}
          title="Let AI rewrite the code to fix detected issues"
        >
          ⚡ Fix My Code
        </button>
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
