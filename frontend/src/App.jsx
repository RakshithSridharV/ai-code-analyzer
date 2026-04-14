import React, { useState } from 'react';
import CodeEditor from './components/CodeEditor';
import AnalysisBoard from './components/AnalysisBoard';
import Chat from './components/Chat';
import HistoryPanel from './components/HistoryPanel';
import AuthModal from './components/AuthModal';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LandingPage from './components/LandingPage';
import './App.css';

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
            <AnalysisBoard
              analysis={analysis}
              isAnalyzing={isAnalyzing}
              originalCode={code}
            />
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
                  />
                </div>
                <div className="compare-board-divider" />
                <div className="glass-panel compare-board-pane">
                  <AnalysisBoard
                    analysis={rightResult}
                    isAnalyzing={isComparingRight}
                    originalCode={rightCode}
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
