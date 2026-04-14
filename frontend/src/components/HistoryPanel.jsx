import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { useAuth } from '../contexts/AuthContext';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export default function HistoryPanel({ onClose }) {
  const { token } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');

  useEffect(() => {
    if (!token) { setLoading(false); return; }
    fetch(`${API}/history`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => {
        if (!res.ok) return Promise.reject('Auth error');
        return res.json();
      })
      .then(data => {
        const chartData = [...(data.history || [])].reverse().map(item => ({
          ...item,
          timeLabel: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }));
        setHistory(chartData);
        setLoading(false);
      })
      .catch(err => {
        setError(typeof err === 'string' ? err : 'Failed to load history.');
        setLoading(false);
      });
  }, [token]);

  return (
    <div className="fix-panel-overlay" onClick={onClose}>
      <div className="fix-panel-modal" style={{ maxWidth: '850px' }} onClick={e => e.stopPropagation()}>
        <div className="fix-panel-header">
          <div className="fix-panel-title">
            <span className="fix-panel-icon">🕒</span>
            My Analysis History
          </div>
          <button className="fix-panel-close" onClick={onClose} title="Close">✕</button>
        </div>

        <div className="fix-panel-body" style={{ flexDirection: 'column', overflowY: 'auto', padding: '1.5rem', gap: '1.5rem' }}>
          {loading ? (
            <div className="fix-loading">
              <div className="fix-spinner" />
              <span>Loading history…</span>
            </div>
          ) : error ? (
            <div className="fix-error">{error}</div>
          ) : history.length === 0 ? (
            <div className="fix-error">No history yet — analyze some code first!</div>
          ) : (
            <>
              {/* Chart */}
              <div className="insight-card" style={{ height: '300px', display: 'flex', flexDirection: 'column', padding: '1.25rem' }}>
                <span className="section-label-block" style={{ marginBottom: '1rem' }}>Quality Score Trend</span>
                <div style={{ flex: 1, minHeight: 0 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={history}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="timeLabel" stroke="#94a3b8" fontSize={12} tickMargin={10} />
                      <YAxis stroke="#94a3b8" fontSize={12} domain={[0, 100]} />
                      <Tooltip
                        contentStyle={{ backgroundColor: 'rgba(18, 21, 34, 0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                        itemStyle={{ color: '#10b981', fontWeight: 600 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="quality_score"
                        stroke="#10b981"
                        strokeWidth={3}
                        dot={{ fill: '#10b981', r: 4, strokeWidth: 0 }}
                        activeDot={{ r: 6, stroke: 'rgba(16, 185, 129, 0.4)', strokeWidth: 4 }}
                        name="Quality Score"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Table */}
              <div className="fn-table-wrap">
                <table className="fn-table">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Language</th>
                      <th>Time Complexity</th>
                      <th>Quality Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...history].reverse().map((item, idx) => (
                      <tr key={idx} className={item.quality_score < 40 ? 'fn-row-bad' : item.quality_score < 70 ? 'fn-row-warn' : 'fn-row-ok'}>
                        <td className="fn-mono" style={{ fontSize: '0.75rem' }}>{new Date(item.timestamp).toLocaleString()}</td>
                        <td style={{ textTransform: 'capitalize', color: 'var(--text-main)', fontSize: '0.8rem' }}>{item.language}</td>
                        <td className="fn-mono">{item.time_complexity}</td>
                        <td>
                          <span className={`fn-score ${item.quality_score < 40 ? 'fn-score-bad' : item.quality_score < 70 ? 'fn-score-warn' : 'fn-score-ok'}`}>
                            {item.quality_score}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
