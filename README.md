# 🧠 AI Code Analyzer

An AI-powered static code analyzer that evaluates **time complexity**, **space complexity**, detects **inefficient coding patterns**, and provides **optimization suggestions** across multiple programming languages.

This project combines **AST-based static analysis** with a **machine learning model** to score code quality and prioritize optimizations.

---

## 🚀 Features

- 🔍 Automatic language detection
- 📊 Time and space complexity estimation
- 🚨 Detection of inefficient patterns:
  - Recursion
  - Inefficient recursion
  - Nested loops
  - Extra memory usage
- 🧠 AI-based code quality prediction
- 🚀 Language-aware optimization suggestions
- 📈 Code quality score (0–100)
- 🌐 Web-based interface with Flask backend

---

## 🧑‍💻 Supported Languages

| Language | Support |
|--------|--------|
| Python | ✅ Full |
| JavaScript | ✅ Full |
| Java | ✅ Full |
| C | ✅ Full |
| C++ | ⚠️ C-subset only |

> **Note:**  
> C++ analysis is limited to the **C subset** of the language. Full STL/template parsing is intentionally not supported to keep the analyzer lightweight and reliable.

---

## 🏗️ Project Structure

```
ai-code-analyzer/
│
├── backend/
│   ├── app.py
│   └── analyzer/
│       ├── language_detector.py
│       ├── java_analyzer.py
│       ├── js_analyzer.py
│       ├── c_analyzer.py
│       ├── cpp_analyzer.py
│       ├── pattern_detector.py
│       ├── feature_extractor.py
│       ├── ai_predictor.py
│       ├── optimization_ranker.py
│       ├── code_optimizer.py
│       ├── quality_score.py
│       └── explanations.py
│
├── data/
│   └── code_quality_dataset.csv
│
├── model/
│   └── code_quality_model.pkl
│
├── frontend/
│   └── index.html
│
├── requirements.txt
└── README.md
```

---

## 🧠 How It Works

1. **Language Detection**
   - Uses syntax and keyword heuristics

2. **Parsing**
   - Python → built-in `ast`
   - Java → `javalang`
   - JavaScript → `pyjsparser`
   - C / C++ → `pycparser` (C subset)

3. **Feature Extraction**
   - Loop depth
   - Recursion detection
   - Memory usage
   - Time and space penalties

4. **AI Prediction**
   - Logistic Regression model trained on labeled complexity data

5. **Optimization Suggestions**
   - Tailored to detected patterns and input language

---

## 📦 Installation

### 1️⃣ Create a virtual environment
```bash
python -m venv .venv
```

### 2️⃣ Activate it

**Windows**
```bash
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

### Start backend
```bash
cd backend
python app.py
```

Backend runs at:
```
http://127.0.0.1:5000
```

### Open frontend
Open `frontend/index.html` in your browser.

---

## 🧪 Example Test Codes

### Python
```python
def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)
```

### JavaScript
```javascript
function fib(n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}
```

### Java
```java
public class Test {
    static int fact(int n) {
        if (n <= 1) return 1;
        return n * fact(n - 1);
    }
}
```

### C
```c
int fact(int n) {
    if (n <= 1) return 1;
    return n * fact(n - 1);
}
```

### C++ (C-subset)
```cpp
int fact(int n) {
    if (n <= 1) return 1;
    return n * fact(n - 1);
}
```

---

## ⚠️ C++ Limitation

C++ code using STL or templates (e.g., `std::vector`, `std::map`) may be detected as C++ but will return **Unknown complexity** due to parser limitations.

This is an intentional design decision to ensure correctness without heavy dependencies like Clang/LLVM.

---

## 📊 Sample Output

```
🔍 CODE ANALYSIS RESULT
🧾 LANGUAGE: JavaScript

📊 Time Complexity: O(2^n)
📊 Space Complexity: O(n)

🚨 DETECTED PATTERNS
• inefficient recursion
• extra memory

📈 QUALITY SCORE: 20 / 100
```

---

## 🧠 Machine Learning Model

- Model: Logistic Regression
- Features:
  - Loop depth
  - Recursion
  - Extra memory usage
  - Time penalty
  - Space penalty
- Dataset: `data/code_quality_dataset.csv`

---

## 🎯 Design Decisions

- Lightweight and dependency-free parsing
- Defensive analysis with safe fallbacks
- Language-aware optimization suggestions
- Honest reporting when analysis is unsupported

---

## 📌 Future Enhancements

- Regex-based heuristic C++ analysis
- Iterative optimization detection
- Code smell detection
- Exportable analysis reports (PDF)
- Docker deployment

---

## 📜 License

MIT License

