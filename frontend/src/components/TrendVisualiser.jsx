/**
 * TrendVisualiser.jsx
 * ────────────────────
 * Fetches GET /history and renders three Chart.js line charts
 * stacked vertically:
 *   1. Quality Score over time
 *   2. Cyclomatic Complexity over time (with colour zones)
 *   3. Halstead Bug Estimate over time (danger threshold)
 */

import React, { useEffect, useRef, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { useAuth } from '../contexts/AuthContext';

// Register all required Chart.js components (no annotation plugin needed — we
// draw reference lines as extra datasets for maximum compatibility)
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
);

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

// ── Helpers ────────────────────────────────────────────────────────────────────

/** Format an ISO-8601 timestamp → "Apr 14 10:32" */
function fmtDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString('en-US', {
    month: 'short',
    day:   'numeric',
    hour:  '2-digit',
    minute:'2-digit',
    hour12: false,
  }).replace(',', '');
}

// Shared dark-theme chart options factory
function baseOptions({ title, yMin, yMax, yLabel }) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 700, easing: 'easeInOutQuart' },
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: title,
        color: '#e8e8e4',
        font: {
          family: "'JetBrains Mono', monospace",
          size: 13,
          weight: '600',
        },
        padding: { bottom: 14 },
      },
      tooltip: {
        backgroundColor: 'rgba(13,13,11,0.95)',
        borderColor: '#2a2a26',
        borderWidth: 1,
        titleColor: '#c8f060',
        bodyColor: '#b0b0a8',
        titleFont: { family: "'JetBrains Mono', monospace", size: 12 },
        bodyFont:  { family: "'JetBrains Mono', monospace", size: 11 },
        padding: 10,
        callbacks: {
          title(items) {
            return items[0]?.label ?? '';
          },
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#666',
          font: { family: "'JetBrains Mono', monospace", size: 10 },
          maxRotation: 30,
          autoSkip: true,
          maxTicksLimit: 10,
        },
        grid: { color: 'rgba(255,255,255,0.04)' },
      },
      y: {
        min: yMin,
        max: yMax,
        ticks: {
          color: '#666',
          font: { family: "'JetBrains Mono', monospace", size: 10 },
        },
        grid: { color: 'rgba(255,255,255,0.05)' },
        title: {
          display: !!yLabel,
          text: yLabel || '',
          color: '#555',
          font: { family: "'JetBrains Mono', monospace", size: 10 },
        },
      },
    },
  };
}

// Build a flat constant-value dataset used as a horizontal reference line
function refLine({ label, value, color, points }) {
  return {
    label,
    data: points.map(() => value),
    borderColor: color,
    borderWidth: 1.5,
    borderDash: [5, 4],
    pointRadius: 0,
    fill: false,
    tension: 0,
    order: 10,
  };
}

// ── Chart 1 — Quality Score ────────────────────────────────────────────────────
function QualityChart({ labels, scores }) {
  const ctx = useRef(null);

  const gradientFill = (context) => {
    const chart = context.chart;
    const { ctx: c, chartArea } = chart;
    if (!chartArea) return 'transparent';
    const gradient = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
    gradient.addColorStop(0,   'rgba(200,240,96,0.28)');
    gradient.addColorStop(0.6, 'rgba(200,240,96,0.06)');
    gradient.addColorStop(1,   'rgba(200,240,96,0.0)');
    return gradient;
  };

  const data = {
    labels,
    datasets: [
      {
        label: 'Quality Score',
        data: scores,
        borderColor: '#c8f060',
        borderWidth: 2.5,
        pointBackgroundColor: '#c8f060',
        pointRadius: scores.length < 20 ? 4 : 2,
        pointHoverRadius: 6,
        tension: 0.4,
        fill: true,
        backgroundColor: gradientFill,
        order: 1,
      },
    ],
  };

  const opts = baseOptions({ title: '① Quality Score', yMin: 0, yMax: 100, yLabel: 'score' });
  opts.plugins.tooltip.callbacks.label = (item) =>
    ` Score: ${Number(item.raw).toFixed(1)}`;

  return (
    <div style={{ height: 220 }}>
      <Line ref={ctx} data={data} options={opts} />
    </div>
  );
}

// ── Chart 2 — Cyclomatic Complexity ───────────────────────────────────────────
function CyclomaticChart({ labels, scores }) {
  // Build per-point colours: 0-4 green, 5-7 yellow, 8+ red
  const pointColours = scores.map((v) =>
    v === null ? 'transparent' : v <= 4 ? '#4ade80' : v <= 7 ? '#facc15' : '#f87171'
  );

  const data = {
    labels,
    datasets: [
      refLine({ label: 'Low/Moderate threshold',  value: 5, color: 'rgba(250,204,21,0.45)', points: labels }),
      refLine({ label: 'Moderate/High threshold', value: 8, color: 'rgba(248,113,113,0.45)', points: labels }),
      {
        label: 'Cyclomatic Complexity',
        data: scores,
        borderColor: '#a78bfa',
        borderWidth: 2.5,
        segment: {
          borderColor(ctx2) {
            const v = ctx2.p1.parsed.y;
            if (v === null) return '#a78bfa';
            return v <= 4 ? '#4ade80' : v <= 7 ? '#facc15' : '#f87171';
          },
        },
        pointBackgroundColor: pointColours,
        pointRadius: scores.length < 20 ? 4 : 2,
        pointHoverRadius: 6,
        tension: 0.4,
        fill: false,
        order: 1,
        spanGaps: true,
      },
    ],
  };

  const opts = baseOptions({ title: '② Cyclomatic Complexity', yMin: 0, yMax: 20, yLabel: 'complexity' });
  opts.plugins.tooltip.callbacks.label = (item) => {
    if (item.datasetIndex < 2) return null; // hide ref-line entries in tooltip
    const v = item.raw;
    if (v === null) return ' n/a (non-Python)';
    const zone = v <= 4 ? 'Simple' : v <= 7 ? 'Moderate' : 'Complex';
    return ` Cyclomatic: ${v}  (${zone})`;
  };
  opts.plugins.tooltip.filter = (item) => item.datasetIndex === 2;

  return (
    <div style={{ height: 220 }}>
      <Line data={data} options={opts} />
    </div>
  );
}

// ── Chart 3 — Halstead Bug Estimate ───────────────────────────────────────────
function HalsteadChart({ labels, bugs }) {
  // Segment coloring: red above 0.2, green below
  const data = {
    labels,
    datasets: [
      refLine({ label: 'Danger threshold (0.2)', value: 0.2, color: 'rgba(248,113,113,0.5)', points: labels }),
      {
        label: 'Bug Estimate',
        data: bugs,
        borderColor: '#4ade80',
        borderWidth: 2.5,
        segment: {
          borderColor(ctx2) {
            const v = ctx2.p1.parsed.y;
            return v !== null && v > 0.2 ? '#f87171' : '#4ade80';
          },
        },
        pointBackgroundColor: bugs.map((v) =>
          v === null ? 'transparent' : v > 0.2 ? '#f87171' : '#4ade80'
        ),
        pointRadius: bugs.length < 20 ? 4 : 2,
        pointHoverRadius: 6,
        tension: 0.4,
        fill: false,
        order: 1,
        spanGaps: true,
      },
    ],
  };

  const opts = baseOptions({ title: '③ Halstead Bug Estimate', yMin: 0, yMax: 1.0, yLabel: 'bugs estimated' });
  opts.plugins.tooltip.callbacks.label = (item) => {
    if (item.datasetIndex === 0) return null;
    const v = item.raw;
    if (v === null) return ' n/a (non-Python)';
    return ` Bug Estimate: ${Number(v).toFixed(4)}${v > 0.2 ? '  ⚠ above threshold' : ''}`;
  };
  opts.plugins.tooltip.filter = (item) => item.datasetIndex === 1;

  return (
    <div style={{ height: 220 }}>
      <Line data={data} options={opts} />
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function TrendVisualiser() {
  const { token } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');

  useEffect(() => {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    setLoading(true);
    setError('');
    fetch(`${API}/history`, { headers })
      .then(async (res) => {
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body.error || `HTTP ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        // history arrives newest-first; reverse for chronological display
        const items = (data.history || []).slice().reverse();
        setHistory(items);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <div style={styles.centred}>
        <div style={styles.spinner} />
        <span style={styles.loadingText}>Loading trend data…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.errorBox}>
        <span style={{ fontSize: '1.2rem' }}>⚠</span>
        <span>{error}</span>
        {!token && (
          <span style={{ color: '#c8f060', marginTop: '0.4rem', fontSize: '0.85rem' }}>
            Sign in to view your personal trends.
          </span>
        )}
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div style={styles.centred}>
        <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📈</div>
        <p style={{ color: '#666', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.9rem' }}>
          No history yet. Analyse some code to start tracking trends.
        </p>
      </div>
    );
  }

  const labels           = history.map((r) => fmtDate(r.timestamp));
  const qualityScores    = history.map((r) => r.quality_score ?? null);
  const cyclomaticScores = history.map((r) => r.cyclomatic_score ?? null);
  const halsteadBugs     = history.map((r) => r.halstead_bugs ?? null);

  return (
    <div style={styles.root}>
      {/* Header */}
      <div style={styles.header}>
        <span style={styles.headerIcon}>📈</span>
        <div>
          <div style={styles.headerTitle}>Complexity Trends</div>
          <div style={styles.headerSub}>{history.length} analyses · chronological</div>
        </div>
      </div>

      {/* Charts */}
      <div style={styles.chartsWrap}>
        <div style={styles.chartCard}>
          <QualityChart labels={labels} scores={qualityScores} />
        </div>
        <div style={styles.chartCard}>
          <CyclomaticChart labels={labels} scores={cyclomaticScores} />
        </div>
        <div style={styles.chartCard}>
          <HalsteadChart labels={labels} bugs={halsteadBugs} />
        </div>
      </div>

      {/* Legend strip */}
      <div style={styles.legend}>
        <LegendDot color="#4ade80" label="Low / Safe" />
        <LegendDot color="#facc15" label="Moderate" />
        <LegendDot color="#f87171" label="High / Danger" />
        <div style={{ marginLeft: 'auto', color: '#444', fontSize: '0.75rem', fontFamily: "'JetBrains Mono', monospace" }}>
          Cyclomatic & Halstead only for Python analyses
        </div>
      </div>
    </div>
  );
}

function LegendDot({ color, label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
      <div style={{ width: 10, height: 10, borderRadius: '50%', background: color, flexShrink: 0 }} />
      <span style={{ color: '#666', fontSize: '0.75rem', fontFamily: "'JetBrains Mono', monospace" }}>{label}</span>
    </div>
  );
}

// ── Styles ─────────────────────────────────────────────────────────────────────
const styles = {
  root: {
    background: '#0a0a08',
    padding: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    height: '100%',
    overflowY: 'auto',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.9rem',
    paddingBottom: '1rem',
    borderBottom: '1px solid #1e1e1a',
  },
  headerIcon: { fontSize: '1.6rem' },
  headerTitle: {
    fontFamily: "'JetBrains Mono', monospace",
    fontWeight: 700,
    fontSize: '1rem',
    color: '#e8e8e4',
  },
  headerSub: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.75rem',
    color: '#555',
    marginTop: '0.2rem',
  },
  chartsWrap: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.25rem',
  },
  chartCard: {
    background: '#0d0d0b',
    border: '1px solid #1e1e1a',
    borderRadius: '10px',
    padding: '1.1rem 1.25rem 0.9rem',
  },
  legend: {
    display: 'flex',
    alignItems: 'center',
    gap: '1.25rem',
    padding: '0.75rem 1rem',
    background: '#0d0d0b',
    border: '1px solid #1e1e1a',
    borderRadius: '8px',
  },
  centred: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    gap: '0.75rem',
    padding: '3rem 1rem',
    background: '#0a0a08',
  },
  loadingText: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.88rem',
    color: '#555',
  },
  spinner: {
    width: 32,
    height: 32,
    borderRadius: '50%',
    border: '3px solid rgba(200,240,96,0.2)',
    borderTopColor: '#c8f060',
    animation: 'spin 0.8s linear infinite',
  },
  errorBox: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
    height: '100%',
    padding: '2rem',
    background: '#0a0a08',
    color: '#f87171',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.88rem',
    textAlign: 'center',
  },
};
