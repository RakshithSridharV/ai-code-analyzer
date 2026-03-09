<div align="center">
  <h1>🧠 AI Code Analyzer</h1>
  <p>An advanced, machine-learning-powered algorithmic profiler assessing Big-O complexity, software metrics, and code health.</p>

  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/Scikit--Learn-ML_Model-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/Vanilla_JS-Frontend-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
</div>

<br />

The AI Code Analyzer is more than a linter — it is a **virtual senior engineer**. It utilizes deep Abstract Syntax Tree (AST) parsing, regex heuristics, and a trained Logistic Regression model to evaluate your code's **Time/Space Complexity**, extract deep **Software Metrics**, and provide actionable **Optimization Rewrites**.

---

## ✨ Premium Features

- ⚡ **Multi-Language Support**: Fully analyzes Python, JavaScript, Java, C, and C++ (including STL).
- 🧠 **Algorithmic Profiling**: Deduces `O(N)` Big-O Time & Space complexity dynamically by analyzing loops, nesting bounds, and recursion stacks.
- 📐 **Deep Code Metrics**: Calculates Cyclomatic Complexity, Maintainability Index, Comment Ratios, and Function Counts.
- 🤖 **ML Quality Scoring**: Uses a trained Scikit-Learn `LogisticRegression` model to output a definitive Code Quality Score (0-100) based on mathematical features.
- 💡 **Auto-Remediation**: Detects `O(n^2)` or inefficient recursion anti-patterns and generates fully optimized, copy-pasteable code templates.
- 🎨 **Aurora Glassmorphism UI**: A stunning, hardware-accelerated frontend with Dark/Light modes, Chart.js complexity growth graphs, and interactive particle backgrounds.

---

## 🏗️ Architecture

The project splits the heavy lifting between an API backend and a lightweight, framework-free frontend.

1. **Frontend (`index.html`, `script.js`)**: A responsive UI using LocalStorage for history persistence.
2. **Backend API (`app.py`)**: A Flask orchestrator.
3. **Parsers**: Uses `ast` (Python), `pyjsparser` (JS), `javalang` (Java), `pycparser` (C), and a custom regex-engine for modern C++.
4. **Machine Learning Model (`model/code_quality_model.pkl`)**: Maps codebase features (e.g., loop depth, extra memory usage) to quality metrics.

---

## 🚀 Quick Start (Run Locally)

### Prerequisites
- Python 3.9+

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/ai-code-analyzer.git
cd ai-code-analyzer
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Backend
```bash
cd backend
python app.py
```
*The Flask API will start at `http://127.0.0.1:5000`*

### 5. Open the UI
Simply open `frontend/index.html` in any modern web browser.

---

## 🌐 Deploy Completely Free

### 1. Deploy the Backend (Python/Flask)
Host the Python backend on [Render.com](https://render.com) for free:
1. Connect your repo and create a "Web Service".
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn app:app` *(Make sure to add `gunicorn` to requirements.txt)*.

### 2. Deploy the Frontend (Vercel)
Host the UI on [Vercel](https://vercel.com) for blazing-fast edge delivery:
1. In `src/script.js`, change the `API_URL` variable to point to your new Render backend URL.
2. Connect your repo to Vercel and click "Deploy" (Zero configuration needed for Vanilla JS/HTML).

---

## 🧪 Supported Languages & Parsers

| Language | Support Details | Parsing Engine used |
|----------|----------------|---------------------|
| **Python** | ✅ Full Support | Built-in `ast` module |
| **JavaScript** | ✅ Full Support | `pyjsparser` |
| **Java** | ✅ Full Support | `javalang` |
| **C** | ✅ Full Support | `pycparser` |
| **C++** | ✅ Full Support | Custom Regex Brace-Matching Heuristics |

---

## 📝 License
MIT License. Feel free to use, modify, and build upon this architecture.
