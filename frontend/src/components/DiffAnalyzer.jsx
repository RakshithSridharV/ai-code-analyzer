/**
 * DiffAnalyzer.jsx
 * ─────────────────
 * Two-column code editor layout for comparing "Original" vs "Refactored" code.
 * Calls POST /analyze for both snippets simultaneously, then renders:
 *   - A metrics comparison table (8 rows, color-coded)
 *   - An auto-generated summary sentence
 *   - Warning sentences for any regressions
 */

import React, { useState, useRef } from 'react';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-java';
import 'prismjs/components/prism-c';
import 'prismjs/components/prism-cpp';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

// ── Language options ────────────────────────────────────────────────────────────
const LANG_OPTIONS = [
  { value: 'auto',       label: 'Auto Detect' },
  { value: 'python',     label: 'Python'      },
  { value: 'javascript', label: 'JavaScript'  },
  { value: 'java',       label: 'Java'        },
  { value: 'c',          label: 'C'           },
  { value: 'cpp',        label: 'C++'         },
];

// ── Syntax highlighter (same as main CodeEditor) ───────────────────────────────
function highlight(code, language) {
  let lang = language === 'auto' ? 'javascript' : language;
  try {
    return Prism.highlight(code, Prism.languages[lang] || Prism.languages.javascript, lang);
  } catch {
    return code;
  }
}

// ── API call ───────────────────────────────────────────────────────────────────
async function callAnalyze(code, language, token) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API}/analyze`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ code, language }),
  });
  const data = await res.json();
  if (!res.ok || data.error) throw new Error(data.error || 'Analysis failed');
  return data;
}

// ── Eco grade helper ───────────────────────────────────────────────────────────
function ecoGrade(result) {
  return result?.analysis?.eco_metrics?.grade ?? null;
}

// Grade order for comparison (lower index = better)
const GRADE_ORDER = ['A+', 'A', 'B', 'C', 'D', 'E', 'F'];
function gradeImproved(orig, ref) {
  if (!orig || !ref) return null;
  const oi = GRADE_ORDER.indexOf(orig);
  const ri = GRADE_ORDER.indexOf(ref);
  if (oi === -1 || ri === -1) return null;
  if (ri < oi) return 'better';
  if (ri > oi) return 'worse';
  return 'same';
}

// ── Complexity order (higher index = worse) ────────────────────────────────────
const COMPLEXITY_ORDER = [
  'O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n²)', 'O(n^2)',
  'O(n³)', 'O(n^3)', 'O(2^n)', 'O(n!)', 'Unknown',
];
function complexityDir(orig, ref) {
  const normalise = (s) => (s || 'Unknown').replace(/\s/g, '').toUpperCase()
    .replace('O(N2)', 'O(N²)').replace('O(N^2)', 'O(N²)')
    .replace('O(N3)', 'O(N³)').replace('O(N^3)', 'O(N³)');
  const n = (s) => normalise(s);
  const oi = COMPLEXITY_ORDER.findIndex(x => n(x) === n(orig));
  const ri = COMPLEXITY_ORDER.findIndex(x => n(x) === n(ref));
  if (oi === -1 || ri === -1) return 'same';
  if (ri < oi) return 'better';
  if (ri > oi) return 'worse';
  return 'same';
}

// ── Numeric delta helper ───────────────────────────────────────────────────────
function numDelta(orig, ref, lowerIsBetter = true) {
  if (orig == null || ref == null) return { dir: 'same', label: 'N/A' };
  const delta = ref - orig;
  if (delta === 0) return { dir: 'same', label: '—' };
  const pct = orig !== 0 ? Math.round((delta / Math.abs(orig)) * 100) : null;
  const sign = delta > 0 ? '+' : '';
  const pctStr = pct !== null ? ` (${sign}${pct}%)` : '';
  const label = `${sign}${Number.isInteger(delta) ? delta : delta.toFixed(4)}${pctStr}`;
  const improved = lowerIsBetter ? delta < 0 : delta > 0;
  return { dir: improved ? 'better' : 'worse', label };
}

// ── Change cell renderer ───────────────────────────────────────────────────────
function ChangeCell({ dir, label, isFixed = false }) {
  if (dir === 'better' || isFixed) {
    return <td style={styles.cellBetter}>{isFixed ? '✅ Fixed' : label === '—' ? '✅ Improved' : `✅ ${label}`}</td>;
  }
  if (dir === 'worse') {
    return <td style={styles.cellWorse}>{`⚠ ${label}`}</td>;
  }
  return <td style={styles.cellSame}>{label || '—'}</td>;
}

// ── Mini code editor pane ─────────────────────────────────────────────────────
function CodePane({ label, code, setCode, language, setLanguage, accentColor }) {
  const EditorComponent = Editor.default || Editor;
  return (
    <div style={styles.pane}>
      {/* Pane header */}
      <div style={{ ...styles.paneHeader, borderTopColor: accentColor }}>
        <span style={{ ...styles.paneLabel, color: accentColor }}>{label}</span>
        <select
          style={styles.langSelect}
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          {LANG_OPTIONS.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {/* Editor */}
      <div style={styles.editorWrap}>
        <EditorComponent
          value={code}
          onValueChange={setCode}
          highlight={(c) => highlight(c, language)}
          padding={14}
          style={{
            fontFamily: '"JetBrains Mono", monospace',
            fontSize: 13,
            minHeight: '100%',
            background: 'transparent',
            color: '#cbd5e1',
          }}
        />
      </div>
    </div>
  );
}

// ── Metrics table ──────────────────────────────────────────────────────────────
function MetricsTable({ orig, ref }) {
  const oA = orig.analysis;
  const rA = ref.analysis;

  // Numeric values
  const oQuality     = orig.quality_score ?? null;
  const rQuality     = ref.quality_score ?? null;
  const oCyclo       = oA?.cyclomatic?.score ?? null;
  const rCyclo       = rA?.cyclomatic?.score ?? null;
  const oHalstead    = oA?.halstead?.bugs_estimated ?? null;
  const rHalstead    = rA?.halstead?.bugs_estimated ?? null;
  const oDataFlow    = Array.isArray(oA?.data_flow) ? oA.data_flow.length : null;  // not returned — use antipatterns length proxy
  const rDataFlow    = Array.isArray(rA?.data_flow) ? rA.data_flow.length : null;

  // data_flow and anti_patterns are top-level on the response object
  const oDF  = Array.isArray(orig.data_flow)    ? orig.data_flow.length    : null;
  const rDF  = Array.isArray(ref.data_flow)      ? ref.data_flow.length     : null;
  const oAP  = Array.isArray(orig.anti_patterns) ? orig.anti_patterns.length : null;
  const rAP  = Array.isArray(ref.anti_patterns)  ? ref.anti_patterns.length  : null;

  // Eco grade
  const oEco = ecoGrade(orig);
  const rEco = ecoGrade(ref);
  const ecoDir = gradeImproved(oEco, rEco)?.toString() ?? 'same';

  // Deltas
  const qualityDelta  = numDelta(oQuality,  rQuality,  false); // higher = better
  const cycloDelta    = numDelta(oCyclo,     rCyclo,    true);  // lower = better
  const halsteadDelta = numDelta(oHalstead,  rHalstead, true);
  const dfDelta       = numDelta(oDF,        rDF,       true);
  const apDelta       = numDelta(oAP,        rAP,       true);

  // Complexity directions
  const timeDir  = complexityDir(oA?.time_complexity,  rA?.time_complexity);
  const spaceDir = complexityDir(oA?.space_complexity, rA?.space_complexity);

  const fmt = (v) => (v == null ? 'N/A' : v);
  const fmtFloat = (v) => (v == null ? 'N/A' : Number(v).toFixed(4));

  return (
    <div style={styles.tableWrap}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Metric</th>
            <th style={styles.th}>Original</th>
            <th style={styles.th}>Refactored</th>
            <th style={styles.th}>Change</th>
          </tr>
        </thead>
        <tbody>
          {/* 1 — Time Complexity */}
          <tr style={styles.tr}>
            <td style={styles.tdLabel}>Time Complexity</td>
            <td style={styles.tdMono}>{fmt(oA?.time_complexity)}</td>
            <td style={styles.tdMono}>{fmt(rA?.time_complexity)}</td>
            <ChangeCell
              dir={timeDir}
              label={timeDir === 'better' ? 'Improved' : timeDir === 'worse' ? 'Regressed' : '—'}
            />
          </tr>

          {/* 2 — Space Complexity */}
          <tr style={styles.tr}>
            <td style={styles.tdLabel}>Space Complexity</td>
            <td style={styles.tdMono}>{fmt(oA?.space_complexity)}</td>
            <td style={styles.tdMono}>{fmt(rA?.space_complexity)}</td>
            <ChangeCell
              dir={spaceDir}
              label={spaceDir === 'better' ? 'Improved' : spaceDir === 'worse' ? 'Regressed' : '—'}
            />
          </tr>

          {/* 3 — Quality Score */}
          <tr style={styles.tr}>
            <td style={styles.tdLabel}>Quality Score</td>
            <td style={styles.tdMono}>{fmt(oQuality)}</td>
            <td style={styles.tdMono}>{fmt(rQuality)}</td>
            <ChangeCell dir={qualityDelta.dir} label={qualityDelta.label} />
          </tr>

          {/* 4 — Cyclomatic Score */}
          <tr style={styles.tr}>
            <td style={styles.tdLabel}>Cyclomatic Score</td>
            <td style={styles.tdMono}>{fmt(oCyclo)}</td>
            <td style={styles.tdMono}>{fmt(rCyclo)}</td>
            <ChangeCell dir={cycloDelta.dir} label={cycloDelta.label} />
          </tr>

          {/* 5 — Halstead Bugs */}
          <tr style={styles.tr}>
            <td style={styles.tdLabel}>Halstead Bugs</td>
            <td style={styles.tdMono}>{fmtFloat(oHalstead)}</td>
            <td style={styles.tdMono}>{fmtFloat(rHalstead)}</td>
            <ChangeCell dir={halsteadDelta.dir} label={halsteadDelta.label} />
          </tr>

          {/* 6 — Eco Rating */}
          <tr style={styles.tr}>
            <td style={styles.tdLabel}>Eco Rating</td>
            <td style={styles.tdMono}>{oEco ?? 'N/A'}</td>
            <td style={styles.tdMono}>{rEco ?? 'N/A'}</td>
            <ChangeCell
              dir={ecoDir}
              label={ecoDir === 'better' ? 'Improved' : ecoDir === 'worse' ? 'Regressed' : '—'}
            />
          </tr>

          {/* 7 — Data Flow Issues */}
          <tr style={styles.tr}>
            <td style={styles.tdLabel}>Data Flow Issues</td>
            <td style={styles.tdMono}>{fmt(oDF)}</td>
            <td style={styles.tdMono}>{fmt(rDF)}</td>
            <ChangeCell
              dir={dfDelta.dir}
              label={dfDelta.label}
              isFixed={rDF === 0 && oDF != null && oDF > 0}
            />
          </tr>

          {/* 8 — Anti-Patterns */}
          <tr style={styles.tr}>
            <td style={styles.tdLabel}>Anti-Patterns</td>
            <td style={styles.tdMono}>{fmt(oAP)}</td>
            <td style={styles.tdMono}>{fmt(rAP)}</td>
            <ChangeCell
              dir={apDelta.dir}
              label={apDelta.label}
              isFixed={rAP === 0 && oAP != null && oAP > 0}
            />
          </tr>
        </tbody>
      </table>
    </div>
  );
}

// ── Summary sentences ──────────────────────────────────────────────────────────
function Summary({ orig, ref }) {
  const oA = orig.analysis;
  const rA = ref.analysis;

  const timeDir  = complexityDir(oA?.time_complexity,  rA?.time_complexity);
  const spaceDir = complexityDir(oA?.space_complexity, rA?.space_complexity);

  const oCycloLabel = oA?.cyclomatic?.risk_label ?? null;
  const rCycloLabel = rA?.cyclomatic?.risk_label ?? null;

  const oDF  = Array.isArray(orig.data_flow) ? orig.data_flow.length : 0;
  const rDF  = Array.isArray(ref.data_flow)  ? ref.data_flow.length  : 0;
  const oAP  = Array.isArray(orig.anti_patterns) ? orig.anti_patterns.length : 0;
  const rAP  = Array.isArray(ref.anti_patterns)  ? ref.anti_patterns.length  : 0;

  const oQuality = orig.quality_score ?? null;
  const rQuality = ref.quality_score  ?? null;

  // Build positive summary parts
  const goods = [];
  if (timeDir === 'better')
    goods.push(`complexity from ${oA?.time_complexity} to ${rA?.time_complexity}`);
  if (spaceDir === 'better')
    goods.push(`space complexity from ${oA?.space_complexity} to ${rA?.space_complexity}`);
  if (oCycloLabel && rCycloLabel && oCycloLabel !== rCycloLabel &&
      complexityDir(oCycloLabel, rCycloLabel) !== 'worse')
    goods.push(`cyclomatic risk from "${oCycloLabel?.split('—')[0]?.trim()}" to "${rCycloLabel?.split('—')[0]?.trim()}"`);
  if (oDF > rDF && rDF === 0) goods.push(`eliminated ${oDF} data flow issue${oDF > 1 ? 's' : ''}`);
  else if (oDF > rDF)         goods.push(`reduced data flow issues from ${oDF} to ${rDF}`);
  if (oAP > rAP && rAP === 0) goods.push(`removed all ${oAP} anti-pattern${oAP > 1 ? 's' : ''}`);
  else if (oAP > rAP)         goods.push(`reduced anti-patterns from ${oAP} to ${rAP}`);
  if (oQuality != null && rQuality != null && rQuality > oQuality)
    goods.push(`improved quality score from ${oQuality} to ${rQuality}`);

  // Build warnings
  const bads = [];
  if (timeDir === 'worse')
    bads.push(`time complexity increased from ${oA?.time_complexity} to ${rA?.time_complexity}`);
  if (spaceDir === 'worse')
    bads.push(`space complexity increased from ${oA?.space_complexity} to ${rA?.space_complexity}`);
  if (oQuality != null && rQuality != null && rQuality < oQuality)
    bads.push(`quality score dropped from ${oQuality} to ${rQuality}`);
  if (rDF > oDF) bads.push(`data flow issues increased from ${oDF} to ${rDF}`);
  if (rAP > oAP) bads.push(`anti-patterns increased from ${oAP} to ${rAP}`);

  // Lines with issues (from data_flow findings)
  const dfLines = Array.isArray(ref.data_flow)
    ? ref.data_flow
        .map(i => i.line)
        .filter(Boolean)
        .slice(0, 5)
    : [];

  const summaryText = goods.length
    ? `Your refactoring ${goods.map((g, i) => {
        if (i === 0 && goods.length > 1) return `improved ${g}`;
        if (i === 0) return `improved ${g}`;
        if (i === goods.length - 1) return `and ${g}`;
        return g;
      }).join(', ')}.`
    : 'No significant improvements detected.';

  return (
    <div style={styles.summaryWrap}>
      {/* Positive */}
      <div style={styles.summaryGood}>
        <span style={styles.summaryIcon}>✦</span>
        <span>{summaryText}</span>
      </div>

      {/* Warnings */}
      {bads.map((b, i) => (
        <div key={i} style={styles.summaryBad}>
          <span style={styles.summaryIcon}>⚠</span>
          <span>
            Warning: {b}.
            {dfLines.length > 0 && i === 0
              ? ` Review lines ${dfLines.join(', ')}.`
              : ''}
          </span>
        </div>
      ))}
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function DiffAnalyzer({ token }) {
  const DEFAULT_ORIG = `def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j] and arr[i] not in duplicates:
                duplicates.append(arr[i])
    return duplicates`;

  const DEFAULT_REF = `def find_duplicates(arr):
    seen = set()
    duplicates = set()
    for item in arr:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)`;

  const [origCode,  setOrigCode]  = useState(DEFAULT_ORIG);
  const [refCode,   setRefCode]   = useState(DEFAULT_REF);
  const [origLang,  setOrigLang]  = useState('python');
  const [refLang,   setRefLang]   = useState('python');

  const [origResult, setOrigResult] = useState(null);
  const [refResult,  setRefResult]  = useState(null);
  const [loading,    setLoading]    = useState(false);
  const [error,      setError]      = useState('');

  const handleCompare = async () => {
    if (!origCode.trim() || !refCode.trim()) {
      setError('Both code panels must have content before comparing.');
      return;
    }
    setLoading(true);
    setError('');
    setOrigResult(null);
    setRefResult(null);

    try {
      const [oRes, rRes] = await Promise.all([
        callAnalyze(origCode, origLang, token),
        callAnalyze(refCode,  refLang,  token),
      ]);
      setOrigResult(oRes);
      setRefResult(rRes);
    } catch (e) {
      setError(e.message || 'Analysis failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.root}>
      {/* ── Editor columns ─────────────────────────────────────────────────── */}
      <div style={styles.editorsRow}>
        <CodePane
          label="Original Code"
          code={origCode}
          setCode={setOrigCode}
          language={origLang}
          setLanguage={setOrigLang}
          accentColor="#94a3b8"
        />

        {/* Divider */}
        <div style={styles.divider}>
          <div style={styles.dividerLine} />
          <div style={styles.dividerBadge}>vs</div>
          <div style={styles.dividerLine} />
        </div>

        <CodePane
          label="Refactored Code"
          code={refCode}
          setCode={setRefCode}
          language={refLang}
          setLanguage={setRefLang}
          accentColor="#c8f060"
        />
      </div>

      {/* ── Compare button ──────────────────────────────────────────────────── */}
      <button
        id="diff-compare-btn"
        style={{
          ...styles.compareBtn,
          opacity: loading ? 0.7 : 1,
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
        onClick={handleCompare}
        disabled={loading}
      >
        {loading ? (
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', justifyContent: 'center' }}>
            <span style={styles.spinner} />
            Analyzing both snippets…
          </span>
        ) : (
          '⚡ Compare Snippets'
        )}
      </button>

      {/* ── Error ──────────────────────────────────────────────────────────── */}
      {error && (
        <div style={styles.errorBox}>
          <span>⚠</span> {error}
        </div>
      )}

      {/* ── Results ────────────────────────────────────────────────────────── */}
      {origResult && refResult && (
        <div style={styles.results}>
          {/* Results header */}
          <div style={styles.resultsHeader}>
            <span style={styles.resultsIcon}>🔍</span>
            <div>
              <div style={styles.resultsTitle}>Diff Analysis Results</div>
              <div style={styles.resultsSub}>
                {origResult.language} → {refResult.language}
              </div>
            </div>
          </div>

          {/* Metrics table */}
          <MetricsTable orig={origResult} ref={refResult} />

          {/* Summary */}
          <Summary orig={origResult} ref={refResult} />
        </div>
      )}
    </div>
  );
}

// ── Styles ─────────────────────────────────────────────────────────────────────
const styles = {
  root: {
    background: '#0a0a08',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    padding: '1.25rem',
    height: '100%',
    overflowY: 'auto',
  },

  // Editors row
  editorsRow: {
    display: 'flex',
    gap: '0',
    flex: '0 0 auto',
    minHeight: 260,
  },
  pane: {
    flex: 1,
    minWidth: 0,
    display: 'flex',
    flexDirection: 'column',
    background: '#0d0d0b',
    border: '1px solid #1e1e1a',
    borderRadius: '10px',
    overflow: 'hidden',
  },
  paneHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0.65rem 1rem',
    borderBottom: '1px solid #1e1e1a',
    borderTop: '2px solid #c8f060',
    background: 'rgba(0,0,0,0.25)',
    flexShrink: 0,
  },
  paneLabel: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.75rem',
    fontWeight: 700,
    letterSpacing: '1px',
    textTransform: 'uppercase',
  },
  langSelect: {
    background: 'rgba(0,0,0,0.4)',
    color: '#94a3b8',
    border: '1px solid rgba(255,255,255,0.08)',
    padding: '0.25rem 0.65rem',
    borderRadius: '6px',
    fontSize: '0.78rem',
    outline: 'none',
    fontFamily: "'JetBrains Mono', monospace",
    cursor: 'pointer',
  },
  editorWrap: {
    flex: 1,
    overflow: 'auto',
    minHeight: 200,
  },

  // Divider
  divider: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    width: 48,
    flexShrink: 0,
    gap: '0.5rem',
    padding: '1rem 0',
  },
  dividerLine: {
    flex: 1,
    width: 1,
    background: 'linear-gradient(to bottom, transparent, rgba(200,240,96,0.25), transparent)',
  },
  dividerBadge: {
    width: 32,
    height: 32,
    borderRadius: '50%',
    background: 'rgba(200,240,96,0.08)',
    border: '1px solid rgba(200,240,96,0.2)',
    color: '#c8f060',
    fontSize: '0.7rem',
    fontWeight: 800,
    letterSpacing: '1px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontFamily: "'JetBrains Mono', monospace",
    textTransform: 'uppercase',
  },

  // Compare button
  compareBtn: {
    width: '100%',
    padding: '0.85rem',
    background: 'linear-gradient(135deg, #c8f060, #8ec820)',
    color: '#0a0a08',
    border: 'none',
    borderRadius: '10px',
    fontFamily: "'JetBrains Mono', monospace",
    fontWeight: 800,
    fontSize: '0.95rem',
    letterSpacing: '0.5px',
    boxShadow: '0 0 24px rgba(200,240,96,0.25)',
    transition: 'all 0.25s cubic-bezier(0.4,0,0.2,1)',
    flexShrink: 0,
  },

  spinner: {
    display: 'inline-block',
    width: 16,
    height: 16,
    borderRadius: '50%',
    border: '2.5px solid rgba(10,10,8,0.25)',
    borderTopColor: '#0a0a08',
    animation: 'spin 0.7s linear infinite',
    flexShrink: 0,
  },

  // Error
  errorBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.6rem',
    padding: '0.85rem 1.1rem',
    background: 'rgba(248,113,113,0.08)',
    border: '1px solid rgba(248,113,113,0.25)',
    borderRadius: '8px',
    color: '#fca5a5',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.85rem',
    flexShrink: 0,
  },

  // Results container
  results: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    animation: 'fadeUp 0.4s ease-out forwards',
  },
  resultsHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.85rem',
    paddingBottom: '0.75rem',
    borderBottom: '1px solid #1e1e1a',
  },
  resultsIcon: { fontSize: '1.4rem' },
  resultsTitle: {
    fontFamily: "'JetBrains Mono', monospace",
    fontWeight: 700,
    fontSize: '0.95rem',
    color: '#e8e8e4',
  },
  resultsSub: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.72rem',
    color: '#555',
    marginTop: '0.15rem',
  },

  // Table
  tableWrap: {
    overflowX: 'auto',
    border: '1px solid #1e1e1a',
    borderRadius: '10px',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.82rem',
  },
  th: {
    padding: '0.65rem 1rem',
    textAlign: 'left',
    fontSize: '0.7rem',
    fontWeight: 700,
    letterSpacing: '0.8px',
    textTransform: 'uppercase',
    color: '#555',
    borderBottom: '1px solid #1e1e1a',
    background: '#0d0d0b',
    whiteSpace: 'nowrap',
  },
  tr: {
    borderBottom: '1px solid rgba(255,255,255,0.03)',
  },
  tdLabel: {
    padding: '0.65rem 1rem',
    color: '#94a3b8',
    fontSize: '0.82rem',
    whiteSpace: 'nowrap',
    fontWeight: 500,
  },
  tdMono: {
    padding: '0.65rem 1rem',
    color: '#c8f060',
    fontFamily: "'JetBrains Mono', monospace",
    whiteSpace: 'nowrap',
  },
  cellBetter: {
    padding: '0.65rem 1rem',
    color: '#4ade80',
    background: 'rgba(74,222,128,0.06)',
    fontWeight: 600,
    whiteSpace: 'nowrap',
  },
  cellWorse: {
    padding: '0.65rem 1rem',
    color: '#f87171',
    background: 'rgba(248,113,113,0.06)',
    fontWeight: 600,
    whiteSpace: 'nowrap',
  },
  cellSame: {
    padding: '0.65rem 1rem',
    color: '#444',
    fontWeight: 400,
    whiteSpace: 'nowrap',
  },

  // Summary
  summaryWrap: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.6rem',
  },
  summaryGood: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '0.65rem',
    padding: '0.9rem 1.1rem',
    background: 'rgba(200,240,96,0.06)',
    border: '1px solid rgba(200,240,96,0.18)',
    borderRadius: '8px',
    color: '#d4f080',
    fontFamily: "'Syne', sans-serif",
    fontSize: '0.88rem',
    lineHeight: 1.6,
  },
  summaryBad: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '0.65rem',
    padding: '0.9rem 1.1rem',
    background: 'rgba(248,113,113,0.06)',
    border: '1px solid rgba(248,113,113,0.2)',
    borderRadius: '8px',
    color: '#fca5a5',
    fontFamily: "'Syne', sans-serif",
    fontSize: '0.88rem',
    lineHeight: 1.6,
  },
  summaryIcon: {
    flexShrink: 0,
    marginTop: '0.1rem',
    color: 'inherit',
  },
};
