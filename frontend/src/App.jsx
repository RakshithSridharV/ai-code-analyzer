import React, { useState } from 'react';
import CodeEditor from './components/CodeEditor';
import AnalysisBoard from './components/AnalysisBoard';
import CFGVisualizer from './components/CFGVisualizer';
import Chat from './components/Chat';
import HistoryPanel from './components/HistoryPanel';
import AuthModal from './components/AuthModal';
import TrendVisualiser from './components/TrendVisualiser';
import DiffAnalyzer from './components/DiffAnalyzer';
import ChallengeMode from './components/ChallengeMode';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LandingPage from './components/LandingPage';
import './App.css';

// ── Challenge solved-count badge (reads from localStorage, no prop drill) ──────
function useSolvedCount() {
  const [count, setCount] = React.useState(() => {
    try {
      const r = JSON.parse(localStorage.getItem('astra_challenge_results') || '{}');
      return Object.values(r).filter(v => v.grade === 'PASS').length;
    } catch { return 0; }
  });
  // Re-read whenever the tab becomes active
  React.useEffect(() => {
    const refresh = () => {
      try {
        const r = JSON.parse(localStorage.getItem('astra_challenge_results') || '{}');
        setCount(Object.values(r).filter(v => v.grade === 'PASS').length);
      } catch {}
    };
    window.addEventListener('storage', refresh);
    window.addEventListener('focus', refresh);
    return () => { window.removeEventListener('storage', refresh); window.removeEventListener('focus', refresh); };
  }, []);
  return count;
}

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

const DEFAULT_PY = `def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)`;

const DEFAULT_JS = `function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}`;

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

// ── Inner app (has access to AuthContext) ─────────────────────────────────────
function AppInner({ onBack }) {
  const { user, token, logout } = useAuth();

  // ── Normal mode state ──────────────────────────────────────────────────────
  const [code, setCode]         = useState(DEFAULT_PY);
  const [language, setLanguage] = useState('auto');
  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // ── UI toggles ─────────────────────────────────────────────────────────────
  const [showHistory, setShowHistory]   = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [compareMode, setCompareMode]   = useState(false);
  const [activeTab, setActiveTab]       = useState('analysis'); // 'analysis' | 'cfg' | 'trends' | 'diff' | 'challenges'

  const solvedCount = useSolvedCount();

  // ── Compare mode state ─────────────────────────────────────────────────────
  const [leftCode,  setLeftCode]   = useState(DEFAULT_PY);
  const [rightCode, setRightCode]  = useState(DEFAULT_JS);
  const [leftLang,  setLeftLang]   = useState('python');
  const [rightLang, setRightLang]  = useState('javascript');
  const [leftResult,  setLeftResult]  = useState(null);
  const [rightResult, setRightResult] = useState(null);
  const [isComparingLeft, setIsComparingLeft] = useState(false);
  const [isComparingRight, setIsComparingRight] = useState(false);
  const isComparingAny = isComparingLeft || isComparingRight;
  const [compareError, setCompareError] = useState('');

  // ── Normal analysis ────────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    setAnalysis(null);
    try {
      const data = await callAnalyze(code, language, token);
      setAnalysis(data);
    } catch (e) {
      alert(e.message || 'Failed to connect to backend');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // ── Compare analysis ───────────────────────────────────────────────────────
  const handleAnalyzeLeft = async () => {
    setIsComparingLeft(true);
    setLeftResult(null);
    setCompareError('');
    try {
      const left = await callAnalyze(leftCode, leftLang, token);
      setLeftResult(left);
    } catch (e) {
      setCompareError(e.message || 'Left analysis failed.');
    } finally {
      setIsComparingLeft(false);
    }
  };

  const handleAnalyzeRight = async () => {
    setIsComparingRight(true);
    setRightResult(null);
    setCompareError('');
    try {
      const right = await callAnalyze(rightCode, rightLang, token);
      setRightResult(right);
    } catch (e) {
      setCompareError(e.message || 'Right analysis failed.');
    } finally {
      setIsComparingRight(false);
    }
  };

  const handleAnalyzeBoth = async () => {
    setIsComparingLeft(true);
    setIsComparingRight(true);
    setLeftResult(null);
    setRightResult(null);
    setCompareError('');
    try {
      const [left, right] = await Promise.all([
        callAnalyze(leftCode, leftLang, token),
        callAnalyze(rightCode, rightLang, token),
      ]);
      setLeftResult(left);
      setRightResult(right);
    } catch (e) {
      setCompareError(e.message || 'One or both analyses failed.');
    } finally {
      setIsComparingLeft(false);
      setIsComparingRight(false);
    }
  };

  // ── Eco comparison sentence ────────────────────────────────────────────────
  const ecoInsight = (() => {
    const lE = leftResult?.analysis?.eco_metrics?.energy_joules_1m;
    const rE = rightResult?.analysis?.eco_metrics?.energy_joules_1m;
    if (lE == null || rE == null) return null;
    if (lE === rE) return `Both languages use equal energy for this algorithm.`;
    const more = lE > rE ? leftLang : rightLang;
    const less = lE > rE ? rightLang : leftLang;
    const ratio = (Math.max(lE, rE) / Math.min(lE, rE)).toFixed(2);
    const diff  = Math.abs(lE - rE).toFixed(4);
    return `${capitalise(more)} uses ${ratio}× more energy than ${capitalise(less)} for this algorithm (Δ ${diff} J per 1M executions).`;
  })();

  function capitalise(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

  const toggleCompare = () => {
    setCompareMode(v => !v);
    setLeftResult(null);
    setRightResult(null);
    setCompareError('');
  };

  const handleLogout = () => {
    logout();
    setShowHistory(false);
  };

  // Resolve the effective language (for CFGVisualizer)
  const effectiveLanguage = (!language || language === 'auto')
    ? (analysis?.language ?? 'python')
    : language;

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="app-container">
      <header className="header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <h1>✦ ASTra</h1>
          <button 
            onClick={onBack} 
            style={{ 
              background: 'transparent', 
              border: '1px solid var(--border)', 
              color: 'var(--text-main)', 
              padding: '0.2rem 0.6rem', 
              borderRadius: '4px', 
              fontSize: '0.8rem', 
              cursor: 'pointer',
              fontFamily: "'Syne', sans-serif"
            }}
          >
            ← Back
          </button>
        </div>

        <div className="header-actions">
          {/* Compare Mode toggle */}
          <button
            className={`fix-btn compare-toggle-btn ${compareMode ? 'compare-toggle-active' : ''}`}
            onClick={toggleCompare}
            title="Side-by-side language comparison"
          >
            {compareMode ? '✕ Exit Compare' : '⇄ Compare Mode'}
          </button>

          {/* History — only shown when logged in */}
          {user && (
            <button
              id="history-btn"
              className="fix-btn history-btn"
              onClick={() => setShowHistory(true)}
              title="View your analysis history"
            >
              🕒 History
            </button>
          )}

          {/* Auth controls */}
          {user ? (
            <div className="auth-user-chip">
              <div className="auth-user-avatar">{user.username.charAt(0).toUpperCase()}</div>
              <span className="auth-user-name">{user.username}</span>
              <button
                id="logout-btn"
                className="auth-logout-btn"
                onClick={handleLogout}
                title="Sign out"
              >
                Sign out
              </button>
            </div>
          ) : (
            <button
              id="login-btn"
              className="fix-btn auth-login-header-btn"
              onClick={() => setShowAuthModal(true)}
              title="Sign in or create account"
            >
              🔐 Sign In
            </button>
          )}
        </div>
      </header>

      {/* ── NORMAL MODE ─────────────────────────────────────────────────────── */}
      {!compareMode && (
        <main className="main-content">
          <div className="glass-panel left-pane">
            <CodeEditor
              code={code} setCode={setCode}
              language={language} setLanguage={setLanguage}
              onAnalyze={handleAnalyze}
              isAnalyzing={isAnalyzing}
            />
          </div>
          <div className="glass-panel right-pane">
            {/* Tab navigation */}
            <div style={{
              display: 'flex',
              gap: '0',
              borderBottom: '1px solid #2a2a26',
              background: '#0d0d0b',
              borderRadius: '8px 8px 0 0',
              overflow: 'hidden',
            }}>
              <button
                id="tab-analysis"
                onClick={() => setActiveTab('analysis')}
                style={{
                  flex: 1,
                  padding: '0.6rem 1rem',
                  background: activeTab === 'analysis' ? '#1a1a16' : 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'analysis' ? '2px solid #c8f060' : '2px solid transparent',
                  color: activeTab === 'analysis' ? '#c8f060' : '#666',
                  fontWeight: activeTab === 'analysis' ? 700 : 400,
                  fontSize: '0.82rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  letterSpacing: '0.04em',
                }}
              >
                📊 Analysis
              </button>
              <button
                id="tab-cfg"
                onClick={() => setActiveTab('cfg')}
                style={{
                  flex: 1,
                  padding: '0.6rem 1rem',
                  background: activeTab === 'cfg' ? '#1a1a16' : 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'cfg' ? '2px solid #c8f060' : '2px solid transparent',
                  color: activeTab === 'cfg' ? '#c8f060' : '#666',
                  fontWeight: activeTab === 'cfg' ? 700 : 400,
                  fontSize: '0.82rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  letterSpacing: '0.04em',
                }}
              >
                ⬡ Control Flow
              </button>
              <button
                id="tab-trends"
                onClick={() => setActiveTab('trends')}
                style={{
                  flex: 1,
                  padding: '0.6rem 1rem',
                  background: activeTab === 'trends' ? '#1a1a16' : 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'trends' ? '2px solid #c8f060' : '2px solid transparent',
                  color: activeTab === 'trends' ? '#c8f060' : '#666',
                  fontWeight: activeTab === 'trends' ? 700 : 400,
                  fontSize: '0.82rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  letterSpacing: '0.04em',
                }}
              >
                📈 Trends
              </button>
              <button
                id="tab-diff"
                onClick={() => setActiveTab('diff')}
                style={{
                  flex: 1,
                  padding: '0.6rem 1rem',
                  background: activeTab === 'diff' ? '#1a1a16' : 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'diff' ? '2px solid #c8f060' : '2px solid transparent',
                  color: activeTab === 'diff' ? '#c8f060' : '#666',
                  fontWeight: activeTab === 'diff' ? 700 : 400,
                  fontSize: '0.82rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  letterSpacing: '0.04em',
                }}
              >
                ⚡ Diff
              </button>
              <button
                id="tab-challenges"
                onClick={() => { setActiveTab('challenges'); }}
                style={{
                  flex: 1,
                  padding: '0.6rem 1rem',
                  background: activeTab === 'challenges' ? '#1a1a16' : 'transparent',
                  border: 'none',
                  borderBottom: activeTab === 'challenges' ? '2px solid #c8f060' : '2px solid transparent',
                  color: activeTab === 'challenges' ? '#c8f060' : '#666',
                  fontWeight: activeTab === 'challenges' ? 700 : 400,
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  letterSpacing: '0.04em',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.35rem',
                }}
              >
                🎯 Challenges
                <span style={{
                  fontSize: '0.65rem',
                  fontFamily: "'JetBrains Mono', monospace",
                  fontWeight: 800,
                  color: activeTab === 'challenges' ? '#c8f060' : '#555',
                  background: activeTab === 'challenges' ? 'rgba(200,240,96,0.15)' : 'rgba(255,255,255,0.06)',
                  border: '1px solid currentColor',
                  borderRadius: 20,
                  padding: '0 0.4rem',
                  lineHeight: '1.5',
                }}>
                  {solvedCount}/10
                </span>
              </button>
            </div>

            {/* Tab content */}
            {activeTab === 'analysis' && (
              <AnalysisBoard
                analysis={analysis}
                isAnalyzing={isAnalyzing}
                originalCode={code}
                code={code}
              />
            )}
            {activeTab === 'cfg' && (
              <div style={{ padding: '0.5rem' }}>
                <CFGVisualizer code={code} language={effectiveLanguage} />
              </div>
            )}
            {activeTab === 'trends' && (
              <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                <TrendVisualiser />
              </div>
            )}
            {activeTab === 'diff' && (
              <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                <DiffAnalyzer token={token} />
              </div>
            )}
            {activeTab === 'challenges' && (
              <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                <ChallengeMode token={token} />
              </div>
            )}
          </div>
        </main>
      )}

      {/* ── COMPARE MODE ──────────────────────────────────────────────────── */}
      {compareMode && (
        <div className="compare-root">
          <div className="compare-editors-row">
            <div className="glass-panel compare-editor-pane">
              <CodeEditor
                code={leftCode}  setCode={setLeftCode}
                language={leftLang}  setLanguage={setLeftLang}
                onAnalyze={handleAnalyzeLeft}
                isAnalyzing={isComparingLeft}
              />
            </div>

            <div className="compare-mid">
              <div className="compare-vs-badge">VS</div>
              <button
                className="analyze-both-btn"
                onClick={handleAnalyzeBoth}
                disabled={isComparingAny}
              >
                {isComparingAny ? (
                  <>
                    <span className="compare-spinner" />
                    Analyzing…
                  </>
                ) : (
                  '⚡ Analyze Both'
                )}
              </button>
            </div>

            <div className="glass-panel compare-editor-pane">
              <CodeEditor
                code={rightCode} setCode={setRightCode}
                language={rightLang} setLanguage={setRightLang}
                onAnalyze={handleAnalyzeRight}
                isAnalyzing={isComparingRight}
              />
            </div>
          </div>

          {(leftResult || rightResult || isComparingAny || compareError) && (
            <div className="compare-results-wrap">
              {compareError && (
                <div className="compare-error">{compareError}</div>
              )}

              <div className="compare-boards-row">
                <div className="glass-panel compare-board-pane">
                  <AnalysisBoard
                    analysis={leftResult}
                    isAnalyzing={isComparingLeft}
                    originalCode={leftCode}
                    code={leftCode}
                  />
                </div>
                <div className="compare-board-divider" />
                <div className="glass-panel compare-board-pane">
                  <AnalysisBoard
                    analysis={rightResult}
                    isAnalyzing={isComparingRight}
                    originalCode={rightCode}
                    code={rightCode}
                  />
                </div>
              </div>

              {ecoInsight && (
                <div className="compare-eco-row">
                  <span className="compare-eco-icon">🌿</span>
                  <span className="compare-eco-text">{ecoInsight}</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <Chat analysisContext={analysis} />

      {showHistory && user && (
        <HistoryPanel onClose={() => setShowHistory(false)} />
      )}

      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} />
      )}
    </div>
  );
}

// ── Root export wrapped in AuthProvider ────────────────────────────────────────
export default function App() {
  const [showApp, setShowApp] = useState(false);

  return (
    <AuthProvider>
      {!showApp ? (
        <LandingPage onEnterApp={() => setShowApp(true)} />
      ) : (
        <AppInner onBack={() => setShowApp(false)} />
      )}
    </AuthProvider>
  );
}
