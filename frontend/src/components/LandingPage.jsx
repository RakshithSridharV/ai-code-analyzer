import React, { useEffect, useState } from 'react';

export default function LandingPage({ onEnterApp }) {
  const [cursorPos, setCursorPos] = useState({ x: -100, y: -100 });
  const [ringPos, setRingPos] = useState({ x: -100, y: -100 });
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    let animFrame;
    let targetX = -100;
    let targetY = -100;
    let currentX = -100;
    let currentY = -100;

    const handleMouseMove = (e) => {
      targetX = e.clientX;
      targetY = e.clientY;
      setCursorPos({ x: targetX, y: targetY });
    };

    const handleMouseOver = (e) => {
      if (e.target.closest('button') || e.target.closest('a') || e.target.closest('.engine-card')) {
        setIsHovering(true);
      } else {
        setIsHovering(false);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseover', handleMouseOver);

    const updateRing = () => {
      currentX += (targetX - currentX) * 0.12;
      currentY += (targetY - currentY) * 0.12;
      setRingPos({ x: currentX, y: currentY });
      animFrame = requestAnimationFrame(updateRing);
    };
    animFrame = requestAnimationFrame(updateRing);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseover', handleMouseOver);
      cancelAnimationFrame(animFrame);
    };
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1 }
    );
    const reveals = document.querySelectorAll('.reveal');
    reveals.forEach((r) => observer.observe(r));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="landing-root">
      <div 
        className="cursor" 
        style={{ 
          left: cursorPos.x, 
          top: cursorPos.y,
          transform: isHovering ? 'translate(-50%, -50%) scale(3)' : 'translate(-50%, -50%) scale(1)'
        }} 
      />
      <div 
        className="cursor-ring" 
        style={{ 
          left: ringPos.x, 
          top: ringPos.y,
          opacity: isHovering ? 0 : 1
        }} 
      />

      <nav className="landing-nav">
        <div className="nav-logo">
          <span className="logo-dot"></span>
          ASTra
        </div>
        <div className="nav-links">
          <a href="#engines">Engines</a>
          <a href="#demo">Demo</a>
          <a href="#about">About</a>
        </div>
        <button className="nav-cta" onClick={onEnterApp}>Launch App →</button>
      </nav>

      <section className="hero">
        <div className="hero-content reveal">
          <div className="hero-eyebrow">
            <span className="eyebrow-line"></span>
            AST-Native Code Intelligence — Built from scratch
          </div>
          <h1 className="hero-title">
            Code analysis that <em>actually</em> understands you
          </h1>
          <p className="hero-subtitle">
            Ten original analysis engines built entirely on Python's AST module. No borrowed logic. Real complexity inference, data-flow tracing, and anti-pattern detection.
          </p>
          <div className="hero-actions">
            <button className="btn-primary" onClick={onEnterApp}>Try ASTra →</button>
            <a href="https://github.com/RakshithSridharV/ai-code-analyzer" target="_blank" rel="noreferrer" className="btn-ghost">View on GitHub</a>
          </div>
        </div>

        <div className="hero-badge reveal">
          Engines written / <span className="badge-value">10</span>
        </div>

        <div className="code-preview reveal">
          <div className="preview-header">fibonacci.py</div>
          <pre className="preview-body">
{`def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)`}
          </pre>
          <div className="preview-footer">
            <span>O(2^n)</span>
            <span>Binary Recursion</span>
            <span>Eco: F</span>
          </div>
        </div>
      </section>

      <section className="marquee reveal">
        <div className="marquee-track">
          <span>InferenceEngine ✦ RecursionClassifier ✦ ExplanationBuilder ✦ DataFlowTracer ✦ AntiPatternDetector ✦ AST-Native Analysis ✦ Zero Borrowed Logic ✦ Python • Java • JS • C ✦</span>
          <span>InferenceEngine ✦ RecursionClassifier ✦ ExplanationBuilder ✦ DataFlowTracer ✦ AntiPatternDetector ✦ AST-Native Analysis ✦ Zero Borrowed Logic ✦ Python • Java • JS • C ✦</span>
        </div>
      </section>

      <section id="engines" className="engines-section">
        <div className="section-header reveal">
          <div>
            <div className="section-label">The Core</div>
            <h2 className="section-title">Ten engines. <em>All original.</em></h2>
          </div>
          <div className="section-count">10</div>
        </div>

        <div className="engines-grid reveal">
          <div className="engine-card">
            <h3>ENGINE 01: InferenceEngine</h3>
            <p className="engine-file">inference_engine.py</p>
            <p className="engine-desc">Infers time and space complexity by walking the AST loop-by-loop. Understands constant vs variable bounds, multiplicative while-loops giving O(log n), and nesting rules.</p>
            <div className="engine-tags">
              <span>Loop Bound Analysis</span><span>Nesting Rules</span><span>Space Detection</span>
            </div>
          </div>
          
          <div className="engine-card">
            <h3>ENGINE 02: RecursionClassifier</h3>
            <p className="engine-file">recursion_classifier.py</p>
            <p className="engine-desc">Classifies recursion pattern: linear, binary, divide-and-conquer, tail-recursive, memoized. Adjusts complexity hint for each.</p>
            <div className="engine-tags">
              <span>Pattern ID</span><span>Tail Detection</span><span>lru_cache Aware</span>
            </div>
          </div>

          <div className="engine-card">
            <h3>ENGINE 03: ExplanationBuilder</h3>
            <p className="engine-file">explanation_builder.py</p>
            <p className="engine-desc">Generates plain-English explanations referencing your actual variable names and line numbers. Deterministic — no LLM involved.</p>
            <div className="engine-tags">
              <span>Deterministic</span><span>Variable-Aware</span><span>Line Numbers</span>
            </div>
          </div>

          <div className="engine-card">
            <h3>ENGINE 04: DataFlowTracer</h3>
            <p className="engine-file">data_flow_tracer.py</p>
            <p className="engine-desc">Flags list membership checks that should be sets, string concatenation in loops, repeated len() calls, sort-then-index patterns.</p>
            <div className="engine-tags">
              <span>List vs Set</span><span>String Concat</span><span>len() Hoisting</span>
            </div>
          </div>

          <div className="engine-card">
            <h3>ENGINE 05: AntiPatternDetector</h3>
            <p className="engine-file">anti_pattern_detector.py</p>
            <p className="engine-desc">Catches mutable default arguments, bare except clauses, global variable modifications, unguarded returns inside loops.</p>
            <div className="engine-tags">
              <span>Mutable Defaults</span><span>Bare Except</span><span>Global State</span>
            </div>
          </div>

          <div className="engine-card built-on-card">
            <h3 className="accent-text">Pure AST / python built-in only</h3>
            <p className="engine-desc mt">Every rule written from scratch using only Python's built-in ast module. No external analysis library.</p>
            <div className="engine-tags">
              <span>20/20 Tests</span><span>Zero deps</span>
            </div>
          </div>
        </div>
      </section>

      <section id="demo" className="demo-section">
        <div className="section-header reveal">
          <div>
            <div className="section-label">See It Works</div>
            <h2 className="section-title">Deep trace <em>in action.</em></h2>
          </div>
        </div>

        <div className="demo-layout reveal">
          <div className="demo-left">
            <div className="preview-header">remove_duplicates.py</div>
            <pre className="preview-body">
{`def remove_duplicates(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result`}
            </pre>
            <button className="btn-primary full-width" onClick={onEnterApp}>Analyze with ASTra</button>
          </div>
          <div className="demo-right">
            <div className="demo-cards flex-row">
              <div className="demo-card metric-val">Time: <span style={{color: 'var(--orange)'}}>O(n²)</span></div>
              <div className="demo-card metric-val">Space: <span>O(n)</span></div>
            </div>
            <div className="demo-card mt">
              <p>remove_duplicates is O(n²) because item loops over items (line 3) and inside it the not in result check scans the entire list each iteration.</p>
            </div>
            <div className="demo-card mt finding-card">
              <div className="finding-severity">HIGH</div>
              <p>'result' is a list — 'in' check is O(n). Convert to set for O(1) lookup.</p>
            </div>
            <div className="demo-card mt eco-card">
              <p>D rating / ~2.4 gCO₂e per 1M executions</p>
            </div>
          </div>
        </div>
      </section>

      <section id="about" className="stats-section reveal">
        <div className="stats">
          <div className="stat-card">
            <div className="stat-number">10</div>
            <div className="stat-label">Original analysis engines written</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">20/20</div>
            <div className="stat-label">Test cases passing</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">0</div>
            <div className="stat-label">External analysis libraries used</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">5</div>
            <div className="stat-label">Languages supported</div>
          </div>
        </div>
      </section>

      <footer className="footer reveal">
        <div className="footer-left">© 2026 ASTra — Final Year Project, CSE</div>
        <div className="footer-right">
          <a href="https://github.com/RakshithSridharV/ai-code-analyzer" target="_blank" rel="noreferrer">GitHub</a>
          <a href="https://github.com/RakshithSridharV/ai-code-analyzer#%F0%9F%94%8C-api-endpoints" target="_blank" rel="noreferrer">API Docs</a>
          <a href="https://github.com/RakshithSridharV/ai-code-analyzer/blob/main/CONTRIBUTING.md" target="_blank" rel="noreferrer">CONTRIBUTING</a>
        </div>
      </footer>
    </div>
  );
}
