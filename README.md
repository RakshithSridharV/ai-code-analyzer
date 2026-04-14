# 🧠 ASTra AI Code Analyzer

[![Python Support](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-blue?style=for-the-badge&logo=react)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/your-username/ai-code-analyzer/ci.yml?style=for-the-badge)](https://github.com/your-username/ai-code-analyzer/actions)

An AI-powered static code analyzer that evaluates **time complexity**, **space complexity**, detects **inefficient coding patterns**, and provides **optimization suggestions** across multiple programming languages.

This project combines **AST-based static analysis** with a **machine learning model** trained on realistic Google MBPP code samples. It features a modern **React frontend**, a **Flask REST API backend**, **Eco-Score carbon footprint tracking**, advanced **Confidence Estimators**, **McCabe's Cyclomatic Complexity**, and full **Docker** containerization.

---

## 🚀 Features

- 🔍 **Automatic language detection** (scoring-based heuristic)
- 📊 **Time and space complexity estimation**
- 🔀 **Cyclomatic Complexity Analyzer** (calculates precise decision paths and assigns testing risk levels)
- 📊 **Confidence Estimator** (displays heuristics and confidence bandwidths for Big-O metrics)
- 🚨 **Detection of inefficient patterns** (recursion, nested loops, extra memory)
- 🧠 **AI-based code quality prediction** (Random Forest trained on Google MBPP data)
- 💬 **AI Chat assistant** (Hugging Face Inference API streaming)
- 🌿 **Green Code / Eco-Score rating** (carbon footprint estimation)
- 🚀 **Language-aware optimization suggestions**
- 📈 **Code quality score** (0–100 scales)
- 🏥 `/health` endpoint for monitoring
- 🛡️ Rate limiting on `/analyze` (30 req/min)
- 🐳 Docker & Docker Compose support

---

## 🧑‍💻 Supported Languages

| Language   | Support          |
|-----------|------------------|
| Python     | ✅ Full          |
| JavaScript | ✅ Full          |
| Java       | ✅ Full          |
| C          | ✅ Full          |
| C++        | ⚠️ C-subset only |

> **Note:**
> C++ analysis is limited to the **C subset** of the language. Full STL/template parsing is intentionally not supported.

---

## 🏗️ Project Structure

```text
ai-code-analyzer/
├── backend/
│   ├── app.py                 # Flask API (analyze, chat, health)
│   ├── ai_chat.py             # HF streaming chat
│   ├── Dockerfile
│   ├── analyzer/
│   │   ├── language_detector.py
│   │   ├── parser.py
│   │   ├── time_complexity.py
│   │   ├── space_complexity.py
│   │   ├── recursion_detector.py
│   │   ├── pattern_detector.py
│   │   ├── cyclomatic_analyzer.py # McCabe's complexity scoring and risk levels
│   │   ├── confidence_estimator.py# Confidence validation heuristic engine
│   │   ├── feature_extractor.py
│   │   ├── ai_predictor.py
│   │   ├── quality_score.py
│   │   ├── code_optimizer.py
│   │   ├── optimization_ranker.py
│   │   ├── explanations.py
│   │   ├── suggestions.py
│   │   ├── java_analyzer.py
│   │   ├── js_analyzer.py
│   │   └── c_analyzer.py
│   ├── ml/
│   │   └── train_model.py
│   └── tests/
│       └── test_analyzer.py
├── frontend/                  # React (Vite) app
│   ├── Dockerfile
│   ├── src/
│   │   ├── components/        # React components (AnalysisBoard, Editor, etc.)
│   │   └── ...
├── data/
│   ├── fetch_real_dataset.py
│   └── code_quality_dataset.csv
├── model/
│   └── code_quality_model.pkl
├── docker-compose.yml
├── requirements.txt
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI workflow
├── CONTRIBUTING.md
└── README.md
```

---

## 📦 Installation

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional)

### Option A: Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-code-analyzer.git
cd ai-code-analyzer

# 2. Backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 3. Frontend
cd frontend
npm install
cd ..

# 4. Environment variables
cp .env.example .env
# Edit .env and add your HF_API_TOKEN
```

### Option B: Docker Compose

```bash
# Create .env with your HF_API_TOKEN
echo "HF_API_TOKEN=hf_your_token_here" > .env

docker-compose up --build
```

- Backend: http://localhost:5000
- Frontend: http://localhost:80

---

## ▶️ Running Locally

### Backend

```bash
cd backend
python app.py
```

Backend runs at http://127.0.0.1:5000

### Frontend (React dev server)

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server runs at http://localhost:5173

---

## 🔌 API Endpoints

| Method | Endpoint       | Description                      |
|--------|---------------|----------------------------------|
| GET    | `/`           | Health text                      |
| GET    | `/health`     | JSON health check                |
| POST   | `/analyze`    | Analyze code (rate-limited)      |
| POST   | `/chat`       | AI chat (SSE streaming)          |
| GET    | `/chat/models`| List available AI models         |

---

## 🧪 Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## 🧠 Machine Learning Model

- **Model**: Random Forest Classifier (with StandardScaler pipeline)
- **Features**: loop_depth, is_recursive, uses_extra_memory, time_penalty, space_penalty
- **Dataset**: `data/code_quality_dataset.csv` (Real human-written Python samples sourced from Google's MBPP dataset via `fetch_real_dataset.py`)

---

## ⚠️ Known Limitations

1. **C++ support**: Limited to C-subset only (no STL, templates, or classes)
2. **Language detection**: Uses heuristic scoring — may occasionally misclassify ambiguous snippets
3. **ML Labeling Proxy**: The model is trained on the MBPP dataset where code correctness (passing tests) is used as a proxy for efficiency. A correct-but-slow $O(n^2)$ solution is labeled as efficient (0), while a buggy $O(n)$ solution is labeled as inefficient (1).

---

## 🎯 Design Decisions

- Lightweight and dependency-free parsing
- Defensive analysis with safe fallbacks
- Explicit confidence interval reporting limits hallucinated estimations
- Language-aware optimization suggestions
- Honest reporting when analysis is unsupported
- Rate limiting to prevent API abuse

---

## 📌 Future Enhancements
- Async task queue (Celery + Redis) for large analyses
- Regex-based heuristic C++ analysis
- Code smell detection
- Exportable analysis reports (PDF)

---

## 📜 License

MIT License
