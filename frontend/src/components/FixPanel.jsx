import React, { useState, useRef, useEffect } from 'react';

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

/**
 * Extracts the first fenced code block content from a markdown string.
 * Falls back to the full trimmed text if no fence is found.
 */
function extractCodeBlock(text) {
  const fenceMatch = text.match(/```[\w]*\n?([\s\S]*?)```/);
  return fenceMatch ? fenceMatch[1].trim() : text.trim();
}

export default function FixPanel({ originalCode, analysis, onClose }) {
  const [fixedCode, setFixedCode]     = useState('');
  const [isLoading, setIsLoading]     = useState(false);
  const [isStreaming, setIsStreaming]  = useState(false);
  const [error, setError]             = useState('');
  const [copied, setCopied]           = useState(false);
  const fixedRef = useRef('');
  const abortRef = useRef(null);

  /* Auto-trigger the fix on mount */
  useEffect(() => {
    requestFix();
    return () => abortRef.current?.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const requestFix = async () => {
    setIsLoading(true);
    setIsStreaming(false);
    setError('');
    setFixedCode('');
    fixedRef.current = '';

    const { patterns = [], language = 'python', analysis: inner = {} } = analysis || {};
    const timeComplexity = inner.time_complexity || 'unknown';

    const systemInstruction =
      `Rewrite the user's exact code to fix the detected issue. ` +
      `Preserve the function name and logic. ` +
      `Return only the fixed code in a code block, no explanation.`;

    const message =
      `Detected issues:\n` +
      `- Patterns: ${patterns.join(', ') || 'none'}\n` +
      `- Time Complexity: ${timeComplexity}\n` +
      `- Language: ${language}\n\n` +
      `Original code:\n\`\`\`${language}\n${originalCode}\n\`\`\``;

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          message,
          history: [],
          analysis_context: analysis,
          system_instruction: systemInstruction,
        }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      setIsLoading(false);
      setIsStreaming(true);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunkText = decoder.decode(value, { stream: true });
        for (const line of chunkText.split('\n')) {
          if (!line.startsWith('data: ')) continue;
          const dataStr = line.slice(6).trim();
          if (dataStr === '[DONE]') continue;
          try {
            const data = JSON.parse(dataStr);
            if (data.content) {
              fixedRef.current += data.content;
              setFixedCode(fixedRef.current);
            }
          } catch (_) {}
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') {
        setError('Failed to reach backend. Make sure the server is running.');
      }
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  const handleCopy = () => {
    const clean = extractCodeBlock(fixedCode);
    navigator.clipboard.writeText(clean).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const displayCode = fixedCode ? extractCodeBlock(fixedCode) : '';

  return (
    <div className="fix-panel-overlay" onClick={onClose}>
      <div className="fix-panel-modal" onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="fix-panel-header">
          <div className="fix-panel-title">
            <span className="fix-panel-icon">⚡</span>
            Fix My Code
          </div>
          <button className="fix-panel-close" onClick={onClose} title="Close">✕</button>
        </div>

        {/* Body — Before / After */}
        <div className="fix-panel-body">

          {/* BEFORE */}
          <div className="fix-pane">
            <div className="fix-pane-label before-label">
              <span className="fix-pane-dot before-dot" />
              Before
            </div>
            <pre className="fix-code-block">{originalCode}</pre>
          </div>

          {/* Divider */}
          <div className="fix-divider">
            <div className="fix-divider-line" />
            <span className="fix-divider-icon">→</span>
            <div className="fix-divider-line" />
          </div>

          {/* AFTER */}
          <div className="fix-pane">
            <div className="fix-pane-label after-label">
              <span className="fix-pane-dot after-dot" />
              After
              {(isLoading || isStreaming) && (
                <span className="fix-streaming-badge">
                  {isLoading ? 'Requesting…' : 'Streaming…'}
                </span>
              )}
            </div>

            {error ? (
              <div className="fix-error">{error}</div>
            ) : isLoading ? (
              <div className="fix-loading">
                <div className="fix-spinner" />
                <span>Generating fix…</span>
              </div>
            ) : (
              <pre className="fix-code-block after-code">
                {displayCode || <span className="fix-placeholder">Fixed code will appear here…</span>}
                {isStreaming && <span className="fix-cursor">▌</span>}
              </pre>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="fix-panel-footer">
          <button
            className="fix-retry-btn"
            onClick={requestFix}
            disabled={isLoading || isStreaming}
          >
            ↺ Regenerate
          </button>
          <button
            className="fix-copy-btn"
            onClick={handleCopy}
            disabled={!displayCode || isLoading || isStreaming}
          >
            {copied ? '✓ Copied!' : '⧉ Copy fixed code'}
          </button>
        </div>

      </div>
    </div>
  );
}
