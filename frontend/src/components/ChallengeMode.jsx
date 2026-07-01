/**
 * ChallengeMode.jsx
 * ───────────────────
 * Two-panel layout:
 *   LEFT  (30%) — challenge list sidebar with status badges
 *   RIGHT (70%) — selected challenge with editor, submit, and results
 *
 * Progress persisted to localStorage under key "astra_challenge_results".
 */

import React, { useState, useEffect, useCallback } from 'react';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';
const LS_KEY = 'astra_challenge_results';

// ── localStorage helpers ───────────────────────────────────────────────────────
function loadResults() {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY) || '{}');
  } catch {
    return {};
  }
}
function saveResults(results) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(results));
  } catch { /* quota exceeded — ignore */ }
}

// ── Grade colours ──────────────────────────────────────────────────────────────
const GRADE_COLOR = {
  PASS:    '#4ade80',
  PARTIAL: '#facc15',
  FAIL:    '#f87171',
};
const GRADE_BG = {
  PASS:    'rgba(74,222,128,0.12)',
  PARTIAL: 'rgba(250,204,21,0.10)',
  FAIL:    'rgba(248,113,113,0.10)',
};
const GRADE_BORDER = {
  PASS:    'rgba(74,222,128,0.3)',
  PARTIAL: 'rgba(250,204,21,0.25)',
  FAIL:    'rgba(248,113,113,0.25)',
};
const GRADE_ICON = { PASS: '✅', PARTIAL: '⚡', FAIL: '❌' };

// ── Sidebar challenge card ─────────────────────────────────────────────────────
function ChallengeCard({ challenge, grade, isActive, onClick }) {
  const color = grade ? GRADE_COLOR[grade] : '#444';
  const bg    = isActive ? 'rgba(200,240,96,0.07)' : 'transparent';
  const border= isActive ? '1px solid rgba(200,240,96,0.3)' : '1px solid transparent';

  return (
    <button
      id={`challenge-card-${challenge.id}`}
      onClick={onClick}
      style={{
        width: '100%',
        textAlign: 'left',
        background: bg,
        border,
        borderRadius: 8,
        padding: '0.75rem 0.9rem',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '0.7rem',
        transition: 'all 0.15s',
        marginBottom: 4,
      }}
    >
      {/* Number badge */}
      <div style={{
        width: 26, height: 26, borderRadius: '50%',
        background: grade ? GRADE_BG[grade] : 'rgba(255,255,255,0.05)',
        border: `1px solid ${color}`,
        color,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '0.7rem', fontWeight: 800, flexShrink: 0,
        fontFamily: "'JetBrains Mono', monospace",
      }}>
        {grade ? GRADE_ICON[grade] : challenge.id}
      </div>

      {/* Text */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontSize: '0.82rem', fontWeight: 600,
          color: isActive ? '#c8f060' : '#c0c0b8',
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>
          {challenge.title}
        </div>
        <div style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: '0.68rem', color: '#555', marginTop: 2,
        }}>
          {challenge.target_complexity}
        </div>
      </div>

      {/* Status dot */}
      {grade && (
        <div style={{
          width: 7, height: 7, borderRadius: '50%',
          background: GRADE_COLOR[grade], flexShrink: 0,
          boxShadow: `0 0 6px ${GRADE_COLOR[grade]}`,
        }} />
      )}
    </button>
  );
}

// ── Test result dots ───────────────────────────────────────────────────────────
function TestDots({ passed, total }) {
  return (
    <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
      {Array.from({ length: total }, (_, i) => (
        <div
          key={i}
          title={i < passed ? 'Passed' : 'Failed'}
          style={{
            width: 12, height: 12, borderRadius: '50%',
            background: i < passed ? '#4ade80' : '#f87171',
            boxShadow: i < passed
              ? '0 0 6px rgba(74,222,128,0.6)'
              : '0 0 6px rgba(248,113,113,0.5)',
          }}
        />
      ))}
      <span style={{
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: '0.8rem',
        color: passed === total ? '#4ade80' : '#f87171',
        marginLeft: 4,
      }}>
        {passed}/{total} tests passed
      </span>
    </div>
  );
}

// ── Grade badge pill ───────────────────────────────────────────────────────────
function GradeBadge({ grade }) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
      padding: '0.3rem 0.85rem',
      background: GRADE_BG[grade],
      border: `1px solid ${GRADE_BORDER[grade]}`,
      borderRadius: 20,
      color: GRADE_COLOR[grade],
      fontFamily: "'JetBrains Mono', monospace",
      fontWeight: 800, fontSize: '0.88rem', letterSpacing: '1px',
    }}>
      {GRADE_ICON[grade]} {grade}
    </span>
  );
}

// ── Right panel — challenge view ───────────────────────────────────────────────
function ChallengeView({ challenge, savedResult, token, onResult }) {
  const EditorComponent = Editor.default || Editor;

  const [code,       setCode]       = useState(challenge.starter_code);
  const [showHint,   setShowHint]   = useState(false);
  const [loading,    setLoading]    = useState(false);
  const [result,     setResult]     = useState(savedResult || null);
  const [error,      setError]      = useState('');

  // Reset state when challenge changes
  useEffect(() => {
    setCode(challenge.starter_code);
    setShowHint(false);
    setResult(savedResult || null);
    setError('');
  }, [challenge.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSubmit = async () => {
    if (!code.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API}/challenges/${challenge.id}/submit`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ code }),
      });
      const data = await res.json();

      if (!res.ok || data.error) throw new Error(data.error || 'Submission failed');

      setResult(data);
      onResult(challenge.id, data.overall_grade, data);
    } catch (e) {
      setError(e.message || 'Failed to connect to backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.rightPanel}>
      {/* ── Challenge header ───────────────────────────────────────────────── */}
      <div style={styles.challengeHeader}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem', flexWrap: 'wrap' }}>
          <span style={styles.challengeNum}>#{challenge.id}</span>
          <h2 style={styles.challengeTitle}>{challenge.title}</h2>
          <span style={styles.complexityBadge}>
            Target: {challenge.target_complexity}
          </span>
        </div>
      </div>

      {/* ── Description + examples ────────────────────────────────────────── */}
      <div style={styles.descBlock}>
        <p style={styles.descText}>{challenge.description}</p>

        <div style={styles.ioRow}>
          <div style={styles.ioCard}>
            <div style={styles.ioLabel}>Example Input</div>
            <code style={styles.ioCode}>{challenge.example_input}</code>
          </div>
          <div style={styles.ioCard}>
            <div style={styles.ioLabel}>Example Output</div>
            <code style={styles.ioCode}>{challenge.example_output}</code>
          </div>
        </div>

        {/* Hint toggle */}
        <button
          style={styles.hintToggle}
          onClick={() => setShowHint(v => !v)}
        >
          {showHint ? '🔼 Hide Hint' : '💡 Show Hint'}
        </button>
        {showHint && (
          <div style={styles.hintBox}>
            <span style={{ marginRight: '0.5rem' }}>💡</span>
            {challenge.hint}
          </div>
        )}
      </div>

      {/* ── Code editor ───────────────────────────────────────────────────── */}
      <div style={styles.editorCard}>
        <div style={styles.editorHeader}>
          <span style={styles.editorLang}>Python</span>
          <span style={{ color: '#444', fontSize: '0.72rem', fontFamily: "'JetBrains Mono', monospace" }}>
            {code.split('\n').length} lines
          </span>
        </div>
        <div style={styles.editorBody}>
          <EditorComponent
            value={code}
            onValueChange={setCode}
            highlight={c => {
              try {
                return Prism.highlight(c, Prism.languages.python, 'python');
              } catch { return c; }
            }}
            padding={14}
            style={{
              fontFamily: '"JetBrains Mono", monospace',
              fontSize: 13,
              minHeight: 180,
              background: 'transparent',
              color: '#cbd5e1',
            }}
          />
        </div>
      </div>

      {/* ── Submit button ──────────────────────────────────────────────────── */}
      <button
        id={`submit-challenge-${challenge.id}`}
        style={{
          ...styles.submitBtn,
          opacity: loading ? 0.7 : 1,
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
        onClick={handleSubmit}
        disabled={loading || !code.trim()}
      >
        {loading ? (
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', justifyContent: 'center' }}>
            <span style={styles.spinner} />
            Evaluating…
          </span>
        ) : (
          '🚀 Submit Solution'
        )}
      </button>

      {/* ── Error ─────────────────────────────────────────────────────────── */}
      {error && (
        <div style={styles.errorBox}>⚠ {error}</div>
      )}

      {/* ── Results panel ─────────────────────────────────────────────────── */}
      {result && (
        <div style={{
          ...styles.resultsPanel,
          borderColor: GRADE_BORDER[result.overall_grade],
          background: GRADE_BG[result.overall_grade],
        }}>
          {/* Grade badge */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <GradeBadge grade={result.overall_grade} />
            <span style={styles.complexityLine}>
              You achieved{' '}
              <code style={{
                ...styles.complexityCode,
                color: result.complexity_achieved ? '#4ade80' : '#f87171',
              }}>
                {result.achieved_complexity}
              </code>
              {' '}— target was{' '}
              <code style={styles.complexityCode}>{result.target_complexity}</code>
            </span>
          </div>

          {/* Test dots */}
          <div style={styles.testDotsRow}>
            <TestDots
              passed={result.tests_passed}
              total={result.tests_total}
            />
          </div>

          {/* Feedback */}
          <div style={styles.feedbackBox}>
            {result.feedback}
          </div>

          {/* Error details on FAIL */}
          {result.overall_grade === 'FAIL' && result.errors?.length > 0 && (
            <div style={styles.errorDetails}>
              {result.errors.slice(0, 3).map((e, i) => (
                <div key={i} style={styles.errorLine}>{e}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function ChallengeMode({ token }) {
  const [challenges,  setChallenges]  = useState([]);
  const [selectedId,  setSelectedId]  = useState(null);
  const [results,     setResults]     = useState(loadResults); // {id: {grade, data}}
  const [loading,     setLoading]     = useState(true);
  const [fetchError,  setFetchError]  = useState('');

  // Fetch challenge list on mount
  useEffect(() => {
    fetch(`${API}/challenges`)
      .then(r => r.json())
      .then(d => {
        const list = d.challenges || [];
        setChallenges(list);
        if (list.length > 0) setSelectedId(list[0].id);
      })
      .catch(e => setFetchError(e.message || 'Failed to load challenges.'))
      .finally(() => setLoading(false));
  }, []);

  // Persist results + update state
  const handleResult = useCallback((challengeId, grade, data) => {
    setResults(prev => {
      const next = { ...prev, [challengeId]: { grade, data } };
      saveResults(next);
      return next;
    });
  }, []);

  const solvedCount = Object.values(results).filter(r => r.grade === 'PASS').length;
  const selected    = challenges.find(c => c.id === selectedId) || null;

  if (loading) {
    return (
      <div style={styles.centred}>
        <div style={styles.spinner} />
        <span style={{ color: '#555', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.85rem' }}>
          Loading challenges…
        </span>
      </div>
    );
  }

  if (fetchError) {
    return (
      <div style={styles.centred}>
        <div style={{ color: '#f87171', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.88rem' }}>
          ⚠ {fetchError}
        </div>
        <div style={{ color: '#444', fontSize: '0.78rem', marginTop: '0.5rem' }}>
          Is the backend running?
        </div>
      </div>
    );
  }

  return (
    <div style={styles.root}>
      {/* ── LEFT SIDEBAR ──────────────────────────────────────────────────── */}
      <aside style={styles.sidebar}>
        {/* Sidebar header */}
        <div style={styles.sidebarHeader}>
          <span style={styles.sidebarTitle}>Challenges</span>
          <span style={styles.solvedBadge}>{solvedCount}/10</span>
        </div>
        <div style={styles.progressBar}>
          <div style={{ ...styles.progressFill, width: `${(solvedCount / 10) * 100}%` }} />
        </div>

        {/* Challenge list */}
        <div style={styles.listScroll}>
          {challenges.map(c => (
            <ChallengeCard
              key={c.id}
              challenge={c}
              grade={results[c.id]?.grade}
              isActive={selectedId === c.id}
              onClick={() => setSelectedId(c.id)}
            />
          ))}
        </div>
      </aside>

      {/* ── RIGHT PANEL ───────────────────────────────────────────────────── */}
      <div style={styles.rightWrap}>
        {selected ? (
          <ChallengeView
            key={selected.id}
            challenge={selected}
            savedResult={results[selected.id]?.data || null}
            token={token}
            onResult={handleResult}
          />
        ) : (
          <div style={styles.centred}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🎯</div>
            <div style={{ color: '#555', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.85rem' }}>
              Select a challenge to begin.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Styles ─────────────────────────────────────────────────────────────────────
const styles = {
  root: {
    display: 'flex',
    height: '100%',
    background: '#0a0a08',
    overflow: 'hidden',
  },

  // Sidebar
  sidebar: {
    width: '30%',
    minWidth: 220,
    maxWidth: 300,
    borderRight: '1px solid #1e1e1a',
    display: 'flex',
    flexDirection: 'column',
    background: '#0d0d0b',
    flexShrink: 0,
  },
  sidebarHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '1rem 1rem 0.5rem',
    flexShrink: 0,
  },
  sidebarTitle: {
    fontFamily: "'JetBrains Mono', monospace",
    fontWeight: 700,
    fontSize: '0.78rem',
    letterSpacing: '1px',
    textTransform: 'uppercase',
    color: '#666',
  },
  solvedBadge: {
    fontFamily: "'JetBrains Mono', monospace",
    fontWeight: 800,
    fontSize: '0.82rem',
    color: '#c8f060',
    background: 'rgba(200,240,96,0.1)',
    border: '1px solid rgba(200,240,96,0.25)',
    padding: '0.15rem 0.55rem',
    borderRadius: 20,
  },
  progressBar: {
    height: 3,
    background: '#1e1e1a',
    margin: '0.5rem 1rem 0.75rem',
    borderRadius: 3,
    overflow: 'hidden',
    flexShrink: 0,
  },
  progressFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #c8f060, #8ec820)',
    borderRadius: 3,
    transition: 'width 0.5s cubic-bezier(0.4,0,0.2,1)',
  },
  listScroll: {
    flex: 1,
    overflowY: 'auto',
    padding: '0 0.6rem 1rem',
  },

  // Right panel wrapper
  rightWrap: {
    flex: 1,
    minWidth: 0,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
  },
  rightPanel: {
    flex: 1,
    overflowY: 'auto',
    padding: '1.25rem 1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },

  // Challenge header
  challengeHeader: {
    paddingBottom: '0.85rem',
    borderBottom: '1px solid #1e1e1a',
  },
  challengeNum: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.78rem',
    color: '#444',
    fontWeight: 700,
  },
  challengeTitle: {
    fontSize: '1.15rem',
    fontWeight: 700,
    color: '#e8e8e4',
    margin: 0,
  },
  complexityBadge: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.72rem',
    fontWeight: 700,
    color: '#c8f060',
    background: 'rgba(200,240,96,0.1)',
    border: '1px solid rgba(200,240,96,0.22)',
    padding: '0.2rem 0.65rem',
    borderRadius: 20,
    whiteSpace: 'nowrap',
  },

  // Description block
  descBlock: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  descText: {
    color: '#94a3b8',
    fontSize: '0.9rem',
    lineHeight: 1.65,
  },
  ioRow: {
    display: 'flex',
    gap: '0.75rem',
    flexWrap: 'wrap',
  },
  ioCard: {
    flex: 1,
    minWidth: 160,
    background: '#111110',
    border: '1px solid #1e1e1a',
    borderRadius: 8,
    padding: '0.7rem 0.9rem',
  },
  ioLabel: {
    fontSize: '0.68rem',
    fontWeight: 700,
    letterSpacing: '0.8px',
    textTransform: 'uppercase',
    color: '#555',
    marginBottom: '0.4rem',
    fontFamily: "'JetBrains Mono', monospace",
  },
  ioCode: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.82rem',
    color: '#a5b4fc',
    wordBreak: 'break-all',
  },
  hintToggle: {
    alignSelf: 'flex-start',
    background: 'rgba(250,204,21,0.08)',
    border: '1px solid rgba(250,204,21,0.2)',
    color: '#facc15',
    borderRadius: 6,
    padding: '0.3rem 0.8rem',
    fontSize: '0.78rem',
    fontWeight: 600,
    cursor: 'pointer',
    fontFamily: "'Syne', sans-serif",
    transition: 'all 0.2s',
  },
  hintBox: {
    background: 'rgba(250,204,21,0.07)',
    border: '1px solid rgba(250,204,21,0.18)',
    borderRadius: 8,
    padding: '0.75rem 1rem',
    color: '#fef08a',
    fontSize: '0.87rem',
    lineHeight: 1.6,
  },

  // Editor
  editorCard: {
    background: '#0d0d0b',
    border: '1px solid #1e1e1a',
    borderRadius: 10,
    overflow: 'hidden',
    flexShrink: 0,
  },
  editorHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0.55rem 0.9rem',
    background: 'rgba(0,0,0,0.25)',
    borderBottom: '1px solid #1e1e1a',
  },
  editorLang: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.72rem',
    fontWeight: 700,
    color: '#c8f060',
    letterSpacing: '0.8px',
    textTransform: 'uppercase',
  },
  editorBody: {
    minHeight: 180,
    maxHeight: 340,
    overflowY: 'auto',
  },

  // Submit
  submitBtn: {
    width: '100%',
    padding: '0.85rem',
    background: 'linear-gradient(135deg, #c8f060, #8ec820)',
    color: '#0a0a08',
    border: 'none',
    borderRadius: 10,
    fontFamily: "'JetBrains Mono', monospace",
    fontWeight: 800,
    fontSize: '0.92rem',
    letterSpacing: '0.5px',
    boxShadow: '0 0 20px rgba(200,240,96,0.2)',
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
    verticalAlign: 'middle',
  },

  errorBox: {
    padding: '0.75rem 1rem',
    background: 'rgba(248,113,113,0.08)',
    border: '1px solid rgba(248,113,113,0.25)',
    borderRadius: 8,
    color: '#fca5a5',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.83rem',
    flexShrink: 0,
  },

  // Results
  resultsPanel: {
    border: '1px solid',
    borderRadius: 10,
    padding: '1.1rem 1.25rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.85rem',
    flexShrink: 0,
  },
  testDotsRow: {
    display: 'flex',
    alignItems: 'center',
  },
  complexityLine: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.8rem',
    color: '#777',
  },
  complexityCode: {
    fontFamily: "'JetBrains Mono', monospace",
    fontWeight: 700,
    fontSize: '0.85rem',
  },
  feedbackBox: {
    fontSize: '0.87rem',
    color: '#b0b0a8',
    lineHeight: 1.65,
    fontFamily: "'Syne', sans-serif",
  },
  errorDetails: {
    background: 'rgba(0,0,0,0.3)',
    borderRadius: 6,
    padding: '0.65rem 0.9rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.3rem',
  },
  errorLine: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '0.75rem',
    color: '#f87171',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-all',
  },

  centred: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.75rem',
    background: '#0a0a08',
    padding: '2rem',
  },
};
