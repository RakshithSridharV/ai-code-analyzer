import React, { useState, useCallback } from 'react';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

// ─── Constants ────────────────────────────────────────────────────────────────

const NODE_WIDTH  = 160;
const NODE_HEIGHT = 50;
const H_SPACING   = 220;
const V_SPACING   = 120;

const EDGE_COLORS = {
  true:       '#c8f060',
  false:      '#f08040',
  loop_back:  '#60a8f0',
  exception:  '#f06060',
  sequential: '#3d3c39',
  return:     '#c8f060',
};

const NODE_ICONS = {
  entry:     '▶',
  exit:      '■',
  condition: '◆',
  loop:      '↻',
  exception: '⚡',
  block:     '□',
};

const NODE_BORDER = {
  entry:     '#c8f060',
  exit:      '#c8f060',
  condition: '#f08040',
  loop:      '#60a8f0',
  exception: '#f06060',
  block:     '#3d3c39',
};

const NODE_TEXT = {
  entry:     '#c8f060',
  exit:      '#c8f060',
  condition: '#f08040',
  loop:      '#60a8f0',
  exception: '#f06060',
  block:     '#b8b5a8',
};

const LEGEND_ITEMS = [
  { color: EDGE_COLORS.sequential, label: 'Sequential',  dashed: false },
  { color: EDGE_COLORS.true,       label: 'True branch', dashed: false },
  { color: EDGE_COLORS.false,      label: 'False branch', dashed: false },
  { color: EDGE_COLORS.loop_back,  label: 'Loop back',   dashed: true  },
  { color: EDGE_COLORS.exception,  label: 'Exception',   dashed: false },
  { color: EDGE_COLORS.return,     label: 'Return',      dashed: true  },
];

// ─── Layout helpers ───────────────────────────────────────────────────────────

function assignLayers(nodes, edges) {
  const layers = {};
  layers['entry'] = 0;

  // BFS from entry
  const queue = ['entry'];
  const visited = new Set(['entry']);

  while (queue.length > 0) {
    const current = queue.shift();
    const currentLayer = layers[current] ?? 0;

    for (const edge of edges) {
      if (edge.from === current && edge.type !== 'loop_back') {
        const target = edge.to;
        if (!visited.has(target)) {
          visited.add(target);
          layers[target] = currentLayer + 1;
          queue.push(target);
        }
      }
    }
  }

  // Any unvisited node → put after max layer
  const maxLayer = Math.max(0, ...Object.values(layers));
  for (const node of nodes) {
    if (layers[node.id] === undefined) {
      layers[node.id] = maxLayer + 1;
    }
  }

  return layers;
}

function computeLayout(nodes, edges) {
  const layers = assignLayers(nodes, edges);

  // Group by layer
  const byLayer = {};
  for (const node of nodes) {
    const l = layers[node.id] ?? 0;
    if (!byLayer[l]) byLayer[l] = [];
    byLayer[l].push(node.id);
  }

  // Assign raw positions
  const nodeList = nodes.map(n => ({ ...n }));
  const idToNode = {};
  for (const n of nodeList) idToNode[n.id] = n;

  for (const [layer, ids] of Object.entries(byLayer)) {
    ids.forEach((id, idx) => {
      idToNode[id].x = parseInt(layer) * H_SPACING;
      idToNode[id].y = idx * V_SPACING;
    });
  }

  // Bounding box
  const allX = nodeList.map(n => n.x);
  const allY = nodeList.map(n => n.y);
  const minX = Math.min(...allX);
  const minY = Math.min(...allY);
  const maxX = Math.max(...allX) + NODE_WIDTH;
  const maxY = Math.max(...allY) + NODE_HEIGHT;

  // Add 40px padding and shift
  const padding  = 40;
  const svgWidth  = Math.max(800, maxX - minX + padding * 2);
  const svgHeight = Math.max(400, maxY - minY + padding * 2);
  const offsetX   = padding - minX;
  const offsetY   = padding - minY;
  nodeList.forEach(n => { n.x += offsetX; n.y += offsetY; });

  // Build positions map
  const positions = {};
  for (const n of nodeList) positions[n.id] = { x: n.x, y: n.y };

  return { positions, svgWidth, svgHeight };
}

// ─── Node component ───────────────────────────────────────────────────────────

function CfgNode({ node, pos }) {
  const { type, label, line } = node;
  const icon    = NODE_ICONS[type]   ?? '□';
  const border  = NODE_BORDER[type]  ?? '#3d3c39';
  const textCol = NODE_TEXT[type]    ?? '#b8b5a8';

  const shortLabel = label.length > 24 ? label.slice(0, 24) + '…' : label;

  if (type === 'condition') {
    // Diamond shape — rotated square
    const cx = pos.x + NODE_WIDTH / 2;
    const cy = pos.y + NODE_HEIGHT / 2;
    const rx = NODE_WIDTH / 2;
    const ry = NODE_HEIGHT / 2;
    const pts = `${cx},${cy - ry} ${cx + rx},${cy} ${cx},${cy + ry} ${cx - rx},${cy}`;
    return (
      <g>
        <polygon points={pts} fill="#1a1a16" stroke={border} strokeWidth="1.5" />
        <text x={cx} y={cy - 6} textAnchor="middle" fill={textCol} fontSize="10" fontWeight="bold">
          {icon} {shortLabel}
        </text>
        {line && (
          <text x={cx} y={cy + 10} textAnchor="middle" fill="#666" fontSize="9">
            L{line}
          </text>
        )}
      </g>
    );
  }

  const rx = type === 'entry' || type === 'exit' ? 27 : 4;
  return (
    <g>
      <rect
        x={pos.x} y={pos.y}
        width={NODE_WIDTH} height={NODE_HEIGHT}
        rx={rx} ry={rx}
        fill="#1a1a16"
        stroke={border}
        strokeWidth="1.5"
      />
      <text x={pos.x + NODE_WIDTH / 2} y={pos.y + 20} textAnchor="middle" fill={textCol} fontSize="11" fontWeight="bold">
        {icon} {shortLabel}
      </text>
      {line && (
        <text x={pos.x + NODE_WIDTH / 2} y={pos.y + 36} textAnchor="middle" fill="#555" fontSize="9">
          line {line}
        </text>
      )}
    </g>
  );
}

// ─── Edge component ───────────────────────────────────────────────────────────

function CfgEdge({ edge, positions }) {
  const fromPos = positions[edge.from];
  const toPos   = positions[edge.to];
  if (!fromPos || !toPos) return null;

  const color   = EDGE_COLORS[edge.type] ?? EDGE_COLORS.sequential;
  const dashed  = edge.type === 'loop_back' || edge.type === 'return';
  const markerId = `arrow-${edge.type}`;

  // Source and target centre points
  const x1 = fromPos.x + NODE_WIDTH / 2;
  const y1 = fromPos.y + NODE_HEIGHT;
  const x2 = toPos.x + NODE_WIDTH / 2;
  const y2 = toPos.y;

  let d;
  if (edge.type === 'loop_back') {
    // Curve widely to the left
    const cx = Math.min(fromPos.x, toPos.x) - 80;
    d = `M ${x1} ${fromPos.y + NODE_HEIGHT / 2} C ${cx} ${fromPos.y + NODE_HEIGHT / 2}, ${cx} ${toPos.y + NODE_HEIGHT / 2}, ${x2} ${toPos.y + NODE_HEIGHT / 2}`;
  } else {
    // Cubic bezier – vertical control points
    const cy1 = y1 + Math.abs(y2 - y1) * 0.4;
    const cy2 = y2 - Math.abs(y2 - y1) * 0.4;
    d = `M ${x1} ${y1} C ${x1} ${cy1}, ${x2} ${cy2}, ${x2} ${y2}`;
  }

  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2;

  return (
    <g>
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeDasharray={dashed ? '5,3' : undefined}
        markerEnd={`url(#${markerId})`}
        opacity="0.85"
      />
      {edge.label && (
        <text x={midX + 4} y={midY - 4} fill={color} fontSize="9" opacity="0.9">
          {edge.label}
        </text>
      )}
    </g>
  );
}

// ─── Arrowhead defs ───────────────────────────────────────────────────────────

function ArrowDefs() {
  return (
    <defs>
      {Object.entries(EDGE_COLORS).map(([type, color]) => (
        <marker
          key={type}
          id={`arrow-${type}`}
          markerWidth="8" markerHeight="8"
          refX="6" refY="3"
          orient="auto"
        >
          <path d="M0,0 L0,6 L8,3 z" fill={color} />
        </marker>
      ))}
    </defs>
  );
}

// ─── Legend ───────────────────────────────────────────────────────────────────

function Legend({ svgHeight }) {
  const legendH = LEGEND_ITEMS.length * 18 + 8;
  const y = svgHeight - legendH - 12;
  return (
    <g transform={`translate(12, ${y})`}>
      <rect x={-4} y={-4} width={130} height={legendH} rx="4"
        fill="#0d0d0b" stroke="#2a2a26" strokeWidth="1" opacity="0.9" />
      {LEGEND_ITEMS.map((item, i) => (
        <g key={item.label} transform={`translate(0, ${i * 18})`}>
          <line
            x1={4} y1={8} x2={26} y2={8}
            stroke={item.color}
            strokeWidth="2"
            strokeDasharray={item.dashed ? '4,2' : undefined}
          />
          <text x={32} y={12} fill="#888" fontSize="10">{item.label}</text>
        </g>
      ))}
    </g>
  );
}

// ─── Stats bar ────────────────────────────────────────────────────────────────

function StatsBar({ cfg }) {
  return (
    <div style={{
      display: 'flex', gap: '1.5rem', padding: '0.6rem 1rem',
      borderBottom: '1px solid #2a2a26', fontSize: '0.82rem', color: '#888',
      background: '#0d0d0b',
    }}>
      <span>
        <span style={{ color: '#c8f060', fontWeight: 'bold' }}>{cfg.function_name}</span>
      </span>
      <span>{cfg.nodes.length} nodes</span>
      <span>{cfg.edges.length} edges</span>
      <span>~{cfg.num_paths} execution path{cfg.num_paths !== 1 ? 's' : ''}</span>
    </div>
  );
}

// ─── Main CFGVisualizer ───────────────────────────────────────────────────────

export default function CFGVisualizer({ code, language }) {
  const [cfg, setCfg]         = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const fetchCfg = useCallback(async () => {
    if (language !== 'python') {
      setError('CFG is only supported for Python');
      setCfg(null);
      return;
    }
    setLoading(true);
    setError(null);
    setCfg(null);
    try {
      const res = await fetch(`${API}/cfg`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      });
      const data = await res.json();
      if (!res.ok || data.error) throw new Error(data.error || 'CFG failed');
      setCfg(data);
    } catch (e) {
      setError(e.message || 'Failed to build CFG');
    } finally {
      setLoading(false);
    }
  }, [code, language]);

  // ── Compute layout ──────────────────────────────────────────────────────────
  const layout = cfg ? computeLayout(cfg.nodes, cfg.edges) : { positions: {}, svgWidth: 800, svgHeight: 400 };
  const { positions, svgWidth, svgHeight } = layout;

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div style={{
      background: '#0a0a08',
      border: '1px solid #2a2a26',
      borderRadius: '8px',
      overflow: 'hidden',
      marginTop: '1rem',
      minHeight: '400px',
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0.75rem 1rem',
        borderBottom: '1px solid #2a2a26',
        background: '#0d0d0b',
      }}>
        <span style={{ fontWeight: 700, fontSize: '0.95rem', color: '#e8e5d8', letterSpacing: '0.02em' }}>
          ⬡ Control Flow Graph
        </span>
        <button
          id="cfg-fetch-btn"
          onClick={fetchCfg}
          disabled={loading}
          style={{
            background: loading ? '#1a1a16' : 'linear-gradient(135deg, #c8f060 0%, #80d040 100%)',
            color: loading ? '#555' : '#0a0a08',
            border: 'none',
            borderRadius: '6px',
            padding: '0.4rem 1rem',
            fontWeight: 700,
            fontSize: '0.82rem',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'opacity 0.2s',
            letterSpacing: '0.04em',
          }}
        >
          {loading ? '⏳ Building…' : '⬡ Fetch CFG'}
        </button>
      </div>

      {/* Stats bar */}
      {cfg && <StatsBar cfg={cfg} />}

      {/* Content */}
      <div style={{ flex: 1, position: 'relative', minHeight: '360px' }}>
        {/* Placeholder */}
        {!cfg && !loading && !error && (
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            color: '#3d3c39', fontSize: '0.9rem', gap: '0.5rem',
          }}>
            <span style={{ fontSize: '2.5rem' }}>⬡</span>
            <span>Analyze Python code to generate its Control Flow Graph</span>
            <span style={{ fontSize: '0.75rem', opacity: 0.6 }}>Scroll to navigate the graph</span>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#c8f060', fontSize: '0.9rem',
          }}>
            <span style={{ animation: 'pulse 1.2s ease-in-out infinite' }}>Building graph…</span>
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#f06060', fontSize: '0.9rem', padding: '1rem', textAlign: 'center',
          }}>
            ⚠ {error}
          </div>
        )}

        {/* SVG Graph — wrapped in scrollable container */}
        {cfg && !loading && (
          <div style={{
            width: '100%',
            height: '100%',
            overflow: 'auto',
            background: '#0a0a08',
            borderRadius: '4px',
          }}>
            <svg
              width={svgWidth}
              height={svgHeight}
              viewBox={`0 0 ${svgWidth} ${svgHeight}`}
              style={{ minWidth: svgWidth, minHeight: svgHeight, display: 'block' }}
            >
              <ArrowDefs />
              {/* Edges (render below nodes) */}
              {cfg.edges.map((edge, i) => (
                <CfgEdge key={i} edge={edge} positions={positions} />
              ))}
              {/* Nodes */}
              {cfg.nodes.map((node) => (
                <CfgNode key={node.id} node={node} pos={positions[node.id] ?? { x: 0, y: 0 }} />
              ))}
              {/* Legend pinned to bottom-left */}
              <Legend svgHeight={svgHeight} />
            </svg>
          </div>
        )}
      </div>
    </div>
  );
}
