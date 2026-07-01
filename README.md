# ASTra — AST-Native Code Intelligence

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-blue?style=for-the-badge&logo=react)](https://react.dev/)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/RakshithSridharV/ai-code-analyzer/test.yml?style=for-the-badge&label=CI)](https://github.com/RakshithSridharV/ai-code-analyzer/actions)

> **10 original analysis engines. Zero borrowed logic.**

ASTra is a static code intelligence platform built from scratch using Python's
built-in `ast` module. Every complexity inference rule, every anti-pattern check,
every explanation — written by hand, not delegated to a library.

---

## What makes this different

Most code analyzers use linters (ESLint, Pylint) or cloud AI. ASTra does neither.
The core analysis runs entirely locally using 10 original AST engines:

| # | Engine | File | What it does |
|---|--------|------|-------------|
| 1 | **InferenceEngine** | `inference_engine.py` | Infers time + space complexity from loop structure. Handles constant bounds (`range(10)` → O(1)), multiplicative while-loops (`i //= 2` → O(log n)), and nested loop multiplication rules |
| 2 | **RecursionClassifier** | `recursion_classifier.py` | Classifies 6 recursion patterns: linear, binary, divide-and-conquer, tail-recursive, memoized, mutual. Adjusts complexity hint for each |
| 3 | **ExplanationBuilder** | `explanation_builder.py` | Generates plain-English explanations referencing your actual variable names and line numbers. Deterministic — no LLM involved |
| 4 | **DataFlowTracer** | `data_flow_tracer.py` | Flags list membership checks that should be sets, string concatenation in loops, repeated `len()` calls, sort-then-index patterns, nested list comprehensions |
| 5 | **AntiPatternDetector** | `anti_pattern_detector.py` | Catches mutable default arguments, bare except clauses, global variable modifications, unguarded returns inside loops, redundant constant assignments |
| 6 | **CyclomaticAnalyzer** | `cyclomatic_analyzer.py` | Implements McCabe's 1976 Cyclomatic Complexity formula. Counts decision points including BoolOp operands. Risk labels from Simple (1-4) to Untestable (16+) |
| 7 | **ConfidenceEstimator** | `confidence_estimator.py` | Adds honest uncertainty bounds to every complexity estimate. Reduces confidence when loop bounds are function calls, suggests alternatives when confidence < 0.85 |
| 8 | **DeadCodeDetector** | `dead_code_detector.py` | Detects unused variables, unused imports, unreachable code after return/raise, and functions defined but never called |
| 9 | **TypeInferencer** | `type_inferencer.py` | Infers variable types statically without running the code. Feeds into DataFlowTracer to catch parameter-level list membership bugs |
| 10 | **HalsteadAnalyzer** | `halstead_analyzer.py` | Implements Halstead's 1977 software science metrics: vocabulary, volume, difficulty, effort, and estimated bug count |

Plus two supporting modules:
- **CFGBuilder** — builds a Control Flow Graph with node/edge types and path counting
- **ReportBuilder** — generates ASCII analysis reports for download

---

## Features

**Analysis**
- Time and space complexity inference (O(1) through O(2^n))
- Cyclomatic complexity with per-function breakdown
- Confidence intervals on every estimate
- Data flow inefficiency detection (5 patterns)
- Anti-pattern detection (5 patterns)
- Dead code detection (5 patterns)
- Static type inference without execution
- Halstead volume, difficulty, and bug estimate
- Control flow graph generation and visualization
- Per-function analysis breakdown
- Carbon footprint / Eco-Score estimation

**Infrastructure**
- Flask REST API with rate limiting (30 req/min on /analyze)
- Security headers via flask-talisman (CSP, HSTS, X-Content-Type-Options)
- Strict CORS origin whitelist
- JWT authentication (register/login/me)
- SQLite history tracking, user-scoped
- SHA-256 code deduplication
- Global error handler — no stack traces leaked to client
- Production/debug mode via FLASK_ENV
- `/health` endpoint for monitoring

**Frontend**
- React + Vite with syntax-highlighted code editor (Prism.js)
- Landing page with engine showcase
- Analysis board: complexity, cyclomatic, confidence bars, findings cards
- Control flow graph SVG visualizer (pan, zoom, colored edges)
- Context-aware AI chat (SSE streaming, analysis result injected into system prompt)
- "Fix it for me" panel — rewrites your code via AI
- History panel with quality score timeline
- Report export (plain-text download)
- Auth modal (register/login)
- DOMPurify XSS protection on all AI-generated markdown

**Languages supported**
| Language | Analyzer | Support |
|----------|----------|---------|
| Python | Built-in `ast` module | Full — all 10 engines |
| JavaScript | Tree-sitter | Full |
| Java | Tree-sitter | Full |
| C | Tree-sitter | Full |
| C++ | Tree-sitter | Full STL/templates |

---

## Architecture

```
ASTra/
├── backend/
│   ├── app.py                          # Flask API — all endpoints
│   ├── ai_chat.py                      # HuggingFace SSE streaming
│   ├── auth.py                         # JWT register/login/me
│   ├── database.py                     # SQLAlchemy Core — users + analyses
│   ├── analyzer/
│   │   ├── inference_engine.py         # Engine 1
│   │   ├── recursion_classifier.py     # Engine 2
│   │   ├── explanation_builder.py      # Engine 3
│   │   ├── data_flow_tracer.py         # Engine 4
│   │   ├── anti_pattern_detector.py    # Engine 5
│   │   ├── cyclomatic_analyzer.py      # Engine 6
│   │   ├── confidence_estimator.py     # Engine 7
│   │   ├── dead_code_detector.py       # Engine 8
│   │   ├── type_inferencer.py          # Engine 9
│   │   ├── halstead_analyzer.py        # Engine 10
│   │   ├── cfg_builder.py              # CFG generation
│   │   ├── report_builder.py           # ASCII report export
│   │   ├── function_splitter.py        # Per-function analysis
│   │   ├── eco_score.py                # Carbon footprint estimation
│   │   ├── language_detector.py        # Weighted scoring detector
│   │   ├── java_analyzer.py            # Tree-sitter Java
│   │   ├── js_analyzer.py              # Tree-sitter JavaScript
│   │   ├── cpp_analyzer.py             # Tree-sitter C++
│   │   └── c_analyzer.py               # Tree-sitter C
│   └── ml/
│       └── train_model.py              # Random Forest training script
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── LandingPage.jsx
│       │   ├── AnalysisBoard.jsx
│       │   ├── CFGVisualizer.jsx
│       │   ├── CodeEditor.jsx
│       │   ├── Chat.jsx
│       │   ├── FixPanel.jsx
│       │   ├── HistoryPanel.jsx
│       │   └── AuthModal.jsx
│       └── contexts/
│           └── AuthContext.jsx
├── data/
│   └── fetch_real_dataset.py           # Downloads Google MBPP dataset
├── model/
│   └── code_quality_model.pkl          # Trained Random Forest model
├── .github/
│   └── workflows/
│       └── test.yml                    # GitHub Actions CI
├── docker-compose.yml
├── requirements.txt
└── CONTRIBUTING.md
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | None | Health text |
| GET | `/health` | None | JSON health check — model_loaded status |
| POST | `/analyze` | Optional JWT | Full analysis (rate-limited 30/min) |
| POST | `/cfg` | None | Control flow graph for Python code |
| POST | `/report` | None | Generate downloadable analysis report |
| POST | `/chat` | None | AI chat via SSE streaming |
| GET | `/chat/models` | None | List available HuggingFace models |
| GET | `/history` | JWT required | Last 50 analyses for authenticated user |
| POST | `/auth/register` | None | Create account |
| POST | `/auth/login` | None | Login, receive JWT |
| GET | `/auth/me` | JWT required | Current user info |

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker + Docker Compose (optional)

### Option A — Manual

```bash
git clone https://github.com/RakshithSridharV/ai-code-analyzer.git
cd ai-code-analyzer

# Backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..

# Environment
cp .env.example .env
# Add your HF_API_TOKEN and a strong JWT_SECRET_KEY to .env
```

### Option B — Docker

```bash
echo "HF_API_TOKEN=hf_your_token_here" > .env
echo "JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" >> .env
docker-compose up --build
```

Backend: http://localhost:5000 | Frontend: http://localhost:80

---

## Running locally

```bash
# Backend
cd backend && python app.py

# Frontend (separate terminal)
cd frontend && npm run dev
# → http://localhost:5173
```

---

## Running tests

```bash
cd backend
python -m pytest tests/ -v --tb=short

# Full engine smoke test
python test_languages.py
```

---

## ML Model

- **Algorithm**: Random Forest Classifier with StandardScaler pipeline
- **Training data**: Google MBPP dataset (real human-written Python code)
- **Labels**: Test pass/fail as efficiency proxy (see Known Limitations)
- **Features**: loop_depth, is_recursive, uses_extra_memory, time_penalty, space_penalty
- **Regenerate**: `python data/fetch_real_dataset.py && python backend/ml/train_model.py`

---

## Known Limitations

1. **Binary search detection**: The InferenceEngine detects O(log n) via multiplicative
   while-loop steps (`i //= 2`, `i *= 2`). Binary search via `lo/hi` convergence requires
   abstract interpretation — a research-level problem outside static analysis scope.

2. **ML labeling proxy**: The Random Forest is trained using test pass/fail as an
   efficiency proxy. A correct-but-slow O(n²) solution scores as efficient (0);
   a buggy O(n) solution scores as inefficient (1). The model measures correctness,
   not true algorithmic efficiency.

3. **`exec()` in dataset fetcher**: `fetch_real_dataset.py` uses `exec()` with a
   2-second SIGALRM timeout to evaluate MBPP test cases. Run only in a trusted
   environment. The SIGALRM timeout does not work on Windows.

4. **Language detection**: Weighted heuristic scoring — may misclassify very short
   or ambiguous snippets.

---

## Security

- All API secrets via environment variables — never hardcoded
- JWT tokens for user authentication (7-day expiry)
- bcrypt password hashing
- flask-talisman security headers (CSP, HSTS, X-Frame-Options)
- DOMPurify sanitization on all AI-generated content
- Rate limiting: 200/day, 50/hour globally; 30/min on /analyze
- Global exception handler — no internal details exposed to clients

---

## License

MIT License
