# Contributing to AI Code Analyzer

Thank you for your interest in contributing! Here's how to get started.

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### 1. Clone and set up the backend

```bash
git clone https://github.com/your-username/ai-code-analyzer.git
cd ai-code-analyzer

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

> **Security Warning**: The data generation script `data/fetch_real_dataset.py` evaluates code snippets using `exec()` without sandboxing. Due to the security risk of arbitrary code execution, this script should **only be run in a trusted environment** and you should verify the dataset URL.

### 2. Set up the frontend

```bash
cd frontend
npm install
```

### 3. Configure environment

```bash
cp .env.example .env
# Add your HF_API_TOKEN to .env
```

> **Never commit `.env`** — it is gitignored. If you accidentally tracked it, run:
> ```bash
> git rm --cached .env
> ```

---

## 🧪 Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

All tests must pass before submitting a PR.

---

## 📝 Coding Guidelines

- **Python**: Follow PEP 8. Use type hints where practical.
- **JavaScript/React**: Use functional components with hooks.
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `chore:`).
- **No large files**: Never commit `node_modules/`, `.venv/`, or binary model files unnecessarily.

---

## 🔄 Pull Request Process

1. Fork the repo and create a feature branch from `main`.
2. Make your changes and add/update tests.
3. Run `pytest` and ensure all tests pass.
4. Submit a PR with a clear description of what changed and why.

---

## 🐳 Docker

To test with Docker:

```bash
docker-compose up --build
```

Backend: http://localhost:5000 | Frontend: http://localhost:80

---

## 📌 Areas That Need Help

- **Real dataset**: Replacing the synthetic `data/code_quality_dataset.csv` with real labeled code samples (~200+ from GitHub).
- **Language detection**: Improving the scoring heuristic for edge cases.
- **Additional languages**: Adding support for Go, Rust, TypeScript, etc.

---

Thank you for contributing! 🙌
