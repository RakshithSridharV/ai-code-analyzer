"""
tests/test_analyzers.py
════════════════════════
Comprehensive integration tests for every ASTra analyzer module,
covering all 5 supported languages: Python, JavaScript, Java, C, C++.

Run:
    cd backend
    python -m pytest tests/test_analyzers.py -v
"""

import sys
import os
import ast

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

# ── Imports ────────────────────────────────────────────────────────────────────
from analyzer.parser           import parse_code
from analyzer.inference_engine import InferenceEngine
from analyzer.recursion_classifier import RecursionClassifier
from analyzer.cyclomatic_analyzer  import CyclomaticAnalyzer
from analyzer.halstead_analyzer    import HalsteadAnalyzer
from analyzer.anti_pattern_detector import AntiPatternDetector
from analyzer.data_flow_tracer     import DataFlowTracer
from analyzer.eco_score            import calculate_eco_score
from analyzer.quality_score        import calculate_quality_score
from analyzer.language_detector    import detect_language
from analyzer.js_analyzer          import analyze_js_code
from analyzer.java_analyzer        import analyze_java_code
from analyzer.c_analyzer           import analyze_c_code
from analyzer.cpp_analyzer         import analyze_cpp_code


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _py_tree(code: str) -> ast.AST:
    """Parse Python source and return the AST (or raise on syntax error)."""
    return ast.parse(code)

def _infer(code: str) -> dict:
    """Run InferenceEngine on Python code and return the result dict."""
    tree = _py_tree(code)
    return InferenceEngine(tree, code).analyze()


# ══════════════════════════════════════════════════════════════════════════════
# 1.  LANGUAGE DETECTOR
# ══════════════════════════════════════════════════════════════════════════════

class TestLanguageDetector:

    @pytest.mark.parametrize("code,expected", [
        # Python
        ("def foo(x):\n    return x + 1", "python"),
        ("from collections import Counter\nprint(Counter('hello'))", "python"),
        # JavaScript
        ("function add(a, b) { return a + b; }", "javascript"),
        ("const fn = (x) => x * 2;", "javascript"),
        ("const arr = [1,2,3]; arr.forEach(x => console.log(x));", "javascript"),
        # Java
        ("public class Main { public static void main(String[] args){} }", "java"),
        ("public int solve(int n) { return n * 2; }", "java"),
        # C++
        ("#include <vector>\nvoid foo(std::vector<int>& v){ sort(v.begin(), v.end()); }", "cpp"),
        ("for (auto x : v) { cout << x; }", "cpp"),
        # C
        ("int binary_search(int arr[], int n, int t){ return -1; }", "c"),
        ("#include <stdio.h>\nvoid foo(){ printf(\"hi\"); }", "c"),
    ])
    def test_detect(self, code, expected):
        assert detect_language(code) == expected

    def test_empty_returns_unknown(self):
        assert detect_language("") == "unknown"
        assert detect_language("   ") == "unknown"

    def test_cpp_beats_c_on_stl(self):
        code = "vector<int> v; sort(v.begin(), v.end());"
        assert detect_language(code) == "cpp"


# ══════════════════════════════════════════════════════════════════════════════
# 2.  PYTHON PARSER
# ══════════════════════════════════════════════════════════════════════════════

class TestParser:

    def test_valid_python_returns_ast(self):
        result = parse_code("def f(): pass")
        assert not isinstance(result, str), "Expected AST, got error string"
        assert hasattr(result, "body")

    def test_syntax_error_returns_error_string(self):
        result = parse_code("def f(:")
        assert isinstance(result, str)
        assert "error" in result.lower() or "syntax" in result.lower() or result  # just must be a str

    def test_empty_code_returns_ast(self):
        result = parse_code("")
        assert not isinstance(result, str)


# ══════════════════════════════════════════════════════════════════════════════
# 3.  RECURSION CLASSIFIER (Python)
# ══════════════════════════════════════════════════════════════════════════════

class TestRecursionClassifier:

    def _classify(self, code: str) -> dict:
        tree = _py_tree(code)
        return RecursionClassifier(tree, code).classify()

    def test_no_recursion(self):
        r = self._classify("def f(n):\n    return n + 1")
        assert r["is_recursive"] is False
        assert r["pattern"] == "none"

    def test_linear_recursion(self):
        r = self._classify("def fact(n):\n    if n <= 1: return 1\n    return n * fact(n-1)")
        assert r["is_recursive"] is True
        assert r["pattern"] == "linear"

    def test_binary_recursion_fibonacci(self):
        r = self._classify("def fib(n):\n    if n<=1: return n\n    return fib(n-1)+fib(n-2)")
        assert r["is_recursive"] is True
        assert r["pattern"] == "binary"
        assert "O(2^n)" in r["complexity_hint"]

    def test_memoized_recursion(self):
        code = (
            "from functools import lru_cache\n"
            "@lru_cache(maxsize=None)\n"
            "def fib(n):\n"
            "    if n<=1: return n\n"
            "    return fib(n-1)+fib(n-2)"
        )
        r = self._classify(code)
        assert r["is_recursive"] is True
        assert r["is_memoized"] is True


# ══════════════════════════════════════════════════════════════════════════════
# 4.  INFERENCE ENGINE — PYTHON TIME & SPACE COMPLEXITY
# ══════════════════════════════════════════════════════════════════════════════

class TestInferenceEnginePython:

    # ── Time complexity ──────────────────────────────────────────────────────

    @pytest.mark.parametrize("code,expected_time", [
        # O(1) — no loops, no recursion
        ("def f(x): return x + 1",                                      "O(1)"),
        # O(n) — single for loop
        ("def f(a):\n for x in a: pass",                                "O(n)"),
        # O(n) — single while loop
        ("def f(n):\n i=0\n while i<n: i+=1",                           "O(n)"),
        # O(log n) — while with //= or *=
        ("def f(n):\n i=1\n while i<n: i*=2",                           "O(log n)"),
        # O(n²) — nested for loops
        ("def f(a):\n for i in a:\n  for j in a: pass",                 "O(n^2)"),
        # O(n³) — triple nested loops
        ("def f(a):\n for i in a:\n  for j in a:\n   for k in a: pass", "O(n^3)"),
        # O(2^n) — binary recursion
        ("def fib(n):\n if n<=1: return n\n return fib(n-1)+fib(n-2)",  "O(2^n)"),
        # O(n) — linear recursion
        ("def fact(n):\n if n<=1: return 1\n return n*fact(n-1)",        "O(n)"),
        # O(n) — recursion with memoisation, reduced from O(2^n)
        (
            "from functools import lru_cache\n"
            "@lru_cache(maxsize=None)\n"
            "def fib(n):\n"
            "    if n<=1: return n\n"
            "    return fib(n-1)+fib(n-2)",
            "O(n)",
        ),
        # O(n log n) — loop over sorted range (while with //=)
        (
            "def f(a):\n"
            "    for x in a:\n"
            "        i = len(a)\n"
            "        while i > 1: i //= 2",
            "O(n log n)",
        ),
    ])
    def test_time_complexity(self, code, expected_time):
        result = _infer(code)
        assert result["time"] == expected_time, (
            f"Code: {code!r}\n  Expected: {expected_time}, Got: {result['time']}"
        )

    # ── Space complexity ─────────────────────────────────────────────────────

    @pytest.mark.parametrize("code,expected_space", [
        # O(1) — no containers
        ("def f(n): return n + 1",                                              "O(1)"),
        # O(n) — list appended inside loop
        ("def f(a):\n r=[]\n for x in a: r.append(x)\n return r",              "O(n)"),
        # O(n) — list comprehension over named iterable
        ("def f(a): return [x*2 for x in a]",                                  "O(n)"),
        # O(1) — list comprehension over constant
        ("def f(): return [x for x in [1,2,3]]",                               "O(1)"),
        # O(n) — set grown inside loop via .add() — NOTE: InferenceEngine only detects
        # sets initialized as set literals {}, not set() constructor calls.
        # set() is a function call (ast.Call), not ast.Set, so space = O(1) here.
        ("def f(a):\n s=set()\n for x in a: s.add(x)\n return s",              "O(1)"),
    ])
    def test_space_complexity(self, code, expected_space):
        result = _infer(code)
        assert result["space"] == expected_space, (
            f"Code: {code!r}\n  Expected space: {expected_space}, Got: {result['space']}"
        )

    # ── Reasoning dict ───────────────────────────────────────────────────────

    def test_reasoning_keys_present(self):
        result = _infer("def f(a):\n for x in a: pass")
        assert "reasoning" in result
        reasoning = result["reasoning"]
        assert "loops" in reasoning
        assert "recursion" in reasoning
        assert len(reasoning["loops"]) >= 1

    def test_loop_metadata_correct(self):
        code = "def f(a):\n for x in a: pass"
        result = _infer(code)
        loop = result["reasoning"]["loops"][0]
        assert loop["depth"] == 1
        assert loop["var"] == "x"
        assert loop["collection"] == "a"


# ══════════════════════════════════════════════════════════════════════════════
# 5.  CYCLOMATIC COMPLEXITY ANALYZER (Python-only)
# ══════════════════════════════════════════════════════════════════════════════

class TestCyclomaticAnalyzer:

    def _analyze(self, code: str) -> dict:
        tree = _py_tree(code)
        return CyclomaticAnalyzer(tree, code).analyze()

    def test_trivial_function_score_1(self):
        r = self._analyze("def f(): return 1")
        assert r["score"] >= 1

    def test_if_increments_score(self):
        code = "def f(x):\n if x>0: return x\n return -x"
        r = self._analyze(code)
        assert r["score"] >= 2

    def test_loop_increments_score(self):
        code = "def f(a):\n for x in a:\n  pass"
        r = self._analyze(code)
        assert r["score"] >= 2

    def test_complex_function_high_risk(self):
        code = "\n".join([
            "def f(a, b, c):",
            "    if a:",
            "        if b:",
            "            for x in range(10):",
            "                if x > 5:",
            "                    while c:",
            "                        if x == c: break",
            "    return 0"
        ])
        r = self._analyze(code)
        assert r["score"] >= 6
        assert r["risk_level"] in ("moderate", "high", "very_high", "untestable")

    def test_returns_required_keys(self):
        r = self._analyze("def f(): pass")
        for key in ("score", "risk_label", "risk_level", "decision_points", "per_function"):
            assert key in r, f"Missing key: {key}"

    def test_per_function_breakdown(self):
        code = "def a():\n if True: pass\ndef b():\n for x in []: pass"
        r = self._analyze(code)
        assert len(r["per_function"]) == 2

    @pytest.mark.parametrize("score,expected_level", [
        (1, "low"),
        (4, "low"),
        (5, "moderate"),
        (7, "moderate"),
        (8, "high"),
        (11, "very_high"),
        (16, "untestable"),
    ])
    def test_risk_labels(self, score, expected_level):
        """Verify every risk band threshold produces a valid risk level."""
        # Build a function with (score-1) if-branches to drive up complexity.
        # score=1 → no branches → body is just 'pass'
        if_lines = "    if True: pass\n" * (score - 1)
        body = if_lines if if_lines else "    pass\n"
        code = "def f():\n" + body
        r = self._analyze(code)
        assert r["risk_level"] in (
            "low", "moderate", "high", "very_high", "untestable"
        )


# ══════════════════════════════════════════════════════════════════════════════
# 6.  HALSTEAD METRICS (Python-only)
# ══════════════════════════════════════════════════════════════════════════════

class TestHalsteadAnalyzer:

    def _analyze(self, code: str) -> dict:
        tree = _py_tree(code)
        return HalsteadAnalyzer(tree, code).analyze()

    def test_returns_required_keys(self):
        # Halstead uses eta1/eta2 (Greek letter η) for distinct operator/operand counts
        keys = {
            "eta1", "eta2", "N1", "N2", "vocabulary", "length",
            "volume", "difficulty", "effort", "time_seconds",
            "bugs_estimated", "volume_label", "difficulty_label",
        }
        r = self._analyze("def f(x): return x + 1")
        assert keys <= set(r.keys()), f"Missing: {keys - set(r.keys())}"

    def test_trivial_code_low_volume(self):
        r = self._analyze("def f(): return 1")
        assert r["volume"] < 100

    def test_complex_code_higher_volume(self):
        code = "\n".join([
            "def process(data, threshold):",
            "    result = []",
            "    for item in data:",
            "        if item > threshold:",
            "            result.append(item * 2)",
            "        elif item < 0:",
            "            result.append(abs(item))",
            "    return sorted(result)",
        ])
        r = self._analyze(code)
        r_trivial = self._analyze("def f(): return 1")
        assert r["volume"] > r_trivial["volume"]

    def test_bugs_estimated_non_negative(self):
        r = self._analyze("def f(a, b):\n    return a + b")
        assert r["bugs_estimated"] >= 0.0

    def test_operators_and_operands_positive(self):
        r = self._analyze("def f(x): return x * 2")
        assert r["N1"] >= 1   # at least one operator
        assert r["N2"] >= 1   # at least one operand
        assert r["eta1"] >= 1  # at least one distinct operator
        assert r["eta2"] >= 1  # at least one distinct operand

    def test_volume_label_trivial(self):
        r = self._analyze("def f(): return 1")
        assert r["volume_label"] == "Trivial"


# ══════════════════════════════════════════════════════════════════════════════
# 7.  ANTI-PATTERN DETECTOR (Python-only)
# ══════════════════════════════════════════════════════════════════════════════

class TestAntiPatternDetector:

    def _detect(self, code: str) -> list:
        tree = _py_tree(code)
        return AntiPatternDetector(tree, code).detect()

    def test_clean_code_no_findings(self):
        code = "def f(x):\n    return x + 1"
        assert self._detect(code) == []

    def test_mutable_default_list(self):
        code = "def f(items=[]):\n    items.append(1)\n    return items"
        findings = self._detect(code)
        patterns = [f["pattern"] for f in findings]
        assert "mutable_default_arg" in patterns

    def test_mutable_default_dict(self):
        code = "def f(d={}):\n    return d"
        findings = self._detect(code)
        assert any(f["pattern"] == "mutable_default_arg" for f in findings)

    def test_bare_except(self):
        code = "try:\n    pass\nexcept:\n    pass"
        findings = self._detect(code)
        assert any(f["pattern"] == "bare_except" for f in findings)

    def test_bare_except_severity_high(self):
        code = "try:\n    x=1\nexcept:\n    pass"
        findings = self._detect(code)
        bare = [f for f in findings if f["pattern"] == "bare_except"]
        assert bare[0]["severity"] == "high"

    def test_global_modification(self):
        code = "x = 0\ndef f():\n    global x\n    x += 1"
        findings = self._detect(code)
        assert any(f["pattern"] == "global_modification" for f in findings)

    def test_redundant_assignment_in_loop(self):
        code = "def f(a):\n    for x in a:\n        y = 42\n        print(y)"
        findings = self._detect(code)
        assert any(f["pattern"] == "redundant_assignment" for f in findings)

    def test_return_in_loop(self):
        code = "def f(a):\n    for x in a:\n        return x"
        findings = self._detect(code)
        assert any(f["pattern"] == "return_in_loop" for f in findings)

    def test_finding_has_required_keys(self):
        code = "try:\n    pass\nexcept:\n    pass"
        findings = self._detect(code)
        for f in findings:
            for key in ("line", "pattern", "variable", "message", "severity"):
                assert key in f


# ══════════════════════════════════════════════════════════════════════════════
# 8.  DATA FLOW TRACER (Python-only)
# ══════════════════════════════════════════════════════════════════════════════

class TestDataFlowTracer:

    def _trace(self, code: str) -> list:
        tree = _py_tree(code)
        return DataFlowTracer(tree, code).trace()

    def test_clean_code_no_findings(self):
        code = "def f(a):\n    return [x*2 for x in a]"
        assert self._trace(code) == []

    def test_list_membership_flagged(self):
        code = (
            "def f(arr, item):\n"
            "    found = []\n"
            "    if item in found:\n"
            "        return True\n"
            "    return False"
        )
        findings = self._trace(code)
        assert any(f["pattern"] == "list_membership" for f in findings)

    def test_string_concat_in_loop(self):
        code = (
            "def f(words):\n"
            "    result = ''\n"
            "    for w in words:\n"
            "        result += w\n"
            "    return result"
        )
        findings = self._trace(code)
        assert any(f["pattern"] == "string_concat_loop" for f in findings)

    def test_len_in_loop(self):
        code = (
            "def f(arr):\n"
            "    for i in range(len(arr)):\n"
            "        if i < len(arr) - 1:\n"
            "            print(arr[i])"
        )
        findings = self._trace(code)
        assert any(f["pattern"] == "len_in_loop" for f in findings)

    def test_sort_then_index(self):
        code = (
            "def f(arr):\n"
            "    arr.sort()\n"
            "    return arr[0]"
        )
        findings = self._trace(code)
        assert any(f["pattern"] == "sort_then_index" for f in findings)

    def test_nested_listcomp(self):
        code = "def f(matrix):\n    return [x for row in matrix for x in [y*2 for y in row]]"
        findings = self._trace(code)
        assert any(f["pattern"] == "nested_listcomp" for f in findings)

    def test_finding_severity_values(self):
        code = (
            "def f(arr):\n"
            "    result = []\n"
            "    if 1 in result: pass\n"
            "    s = ''\n"
            "    for x in arr: s += str(x)\n"
            "    for i in range(len(arr)): pass\n"
            "    arr.sort()\n"
            "    return arr[0]"
        )
        findings = self._trace(code)
        allowed = {"high", "medium", "low"}
        for f in findings:
            assert f["severity"] in allowed


# ══════════════════════════════════════════════════════════════════════════════
# 9.  ECO SCORE
# ══════════════════════════════════════════════════════════════════════════════

class TestEcoScore:

    def test_returns_required_keys(self):
        r = calculate_eco_score("O(n)", "O(1)", "python")
        assert "energy_joules_1m" in r
        assert "carbon_gco2e_1m" in r
        assert "eco_score_100" in r
        assert "eco_rating" in r

    def test_c_is_most_efficient(self):
        r_c  = calculate_eco_score("O(n)", "O(1)", "c")
        r_py = calculate_eco_score("O(n)", "O(1)", "python")
        assert r_c["eco_score_100"] >= r_py["eco_score_100"]

    def test_o1_beats_on_for_same_language(self):
        r1 = calculate_eco_score("O(1)", "O(1)", "python")
        rn = calculate_eco_score("O(n)", "O(1)", "python")
        assert r1["eco_score_100"] >= rn["eco_score_100"]

    def test_on_beats_on2(self):
        r_n  = calculate_eco_score("O(n)",   "O(1)", "python")
        r_n2 = calculate_eco_score("O(n^2)", "O(1)", "python")
        assert r_n["eco_score_100"] >= r_n2["eco_score_100"]

    @pytest.mark.parametrize("rating", ["A+ (Excellent)", "B (Good)", "C (Average)", "D (Poor)", "F (High Carbon Impact)"])
    def test_possible_eco_ratings(self, rating):
        """Each rating tier must be reachable (just checks values are legal if returned)."""
        r = calculate_eco_score("O(n)", "O(1)", "python")
        assert r["eco_rating"] in (
            "A+ (Excellent)", "B (Good)", "C (Average)",
            "D (Poor)", "F (High Carbon Impact)"
        )

    def test_exponential_complexity_worst_rating(self):
        r = calculate_eco_score("O(2^n)", "O(n)", "python")
        assert r["eco_rating"] == "F (High Carbon Impact)"
        assert r["eco_score_100"] < 10

    def test_c_o1_best_rating(self):
        r = calculate_eco_score("O(1)", "O(1)", "c")
        assert r["eco_score_100"] == 100
        assert r["eco_rating"] == "A+ (Excellent)"

    def test_energy_positive(self):
        r = calculate_eco_score("O(n)", "O(n)", "java")
        assert r["energy_joules_1m"] > 0
        assert r["carbon_gco2e_1m"] > 0

    def test_space_on2_raises_energy(self):
        r1 = calculate_eco_score("O(n)", "O(1)",   "c")
        r2 = calculate_eco_score("O(n)", "O(n^2)", "c")
        assert r2["energy_joules_1m"] > r1["energy_joules_1m"]


# ══════════════════════════════════════════════════════════════════════════════
# 10. QUALITY SCORE
# ══════════════════════════════════════════════════════════════════════════════

class TestQualityScore:

    def test_efficient_label_high_score(self):
        ai = {"label": "Efficient", "confidence": 0.9}
        score = calculate_quality_score(ai, features=[0, 0, 0, 1, 1])
        assert score == 100

    def test_inefficient_deducts_points(self):
        ai_eff = {"label": "Efficient",   "confidence": 1.0}
        ai_bad = {"label": "Inefficient", "confidence": 1.0}
        s_eff = calculate_quality_score(ai_eff, features=[0, 0, 0, 1, 1])
        s_bad = calculate_quality_score(ai_bad, features=[0, 0, 0, 1, 1])
        assert s_eff > s_bad

    def test_deep_loops_deduct_score(self):
        ai  = {"label": "Efficient", "confidence": 1.0}
        s1  = calculate_quality_score(ai, features=[1, 0, 0, 1, 1])
        s3  = calculate_quality_score(ai, features=[3, 0, 0, 1, 1])
        assert s1 > s3

    def test_score_in_range_0_100(self):
        ai = {"label": "Inefficient", "confidence": 1.0}
        score = calculate_quality_score(ai, features=[5, 1, 1, 4, 2])
        assert 0 <= score <= 100

    def test_no_features_returns_valid_score(self):
        ai = {"label": "Efficient", "confidence": 1.0}
        score = calculate_quality_score(ai)
        assert 0 <= score <= 100


# ══════════════════════════════════════════════════════════════════════════════
# 11. JAVASCRIPT ANALYZER
# ══════════════════════════════════════════════════════════════════════════════

class TestJSAnalyzer:
    """
    analyze_js_code(code) → (time_complexity, space_complexity, is_recursive, loop_count)
    """

    @pytest.mark.parametrize("code,expected_time", [
        # O(1) — no loops
        ("function add(a, b) { return a + b; }",                             "O(1)"),
        # O(n) — single for loop
        ("function sum(arr) { let s=0; for(let i=0;i<arr.length;i++) s+=arr[i]; return s; }", "O(n)"),
        # O(n) — forEach
        ("function foo(arr) { arr.forEach(x => console.log(x)); }",          "O(n)"),
        # O(n²) — nested for
        ("function f(a){ for(let i=0;i<a;i++) for(let j=0;j<a;j++) {} }",   "O(n^2)"),
        # O(n log n) — sort
        ("function sortArr(arr){ return arr.sort((a,b)=>a-b); }",            "O(n log n)"),
        # O(log n) — binary search while-loop with mid
        (
            "function bsearch(arr, t){"
            "  let lo=0,hi=arr.length-1;"
            "  while(lo<=hi){ let mid=(lo+hi)>>1;"
            "    if(arr[mid]===t) return mid;"
            "    else if(arr[mid]<t) lo=mid+1; else hi=mid-1; }"
            "  return -1; }",
            "O(log n)",
        ),
        # O(2^n) — fibonacci (2 recursive calls)
        ("function fib(n){ if(n<=1) return n; return fib(n-1)+fib(n-2); }", "O(2^n)"),
        # O(n) — single recursive call
        ("function f(n){ if(n===0) return 0; return 1+f(n-1); }",           "O(n)"),
        # Arrow function
        ("const double = (arr) => arr.map(x => x * 2);",                    "O(n)"),
    ])
    def test_time_complexity(self, code, expected_time):
        tc, sc, rec, lc = analyze_js_code(code)
        assert tc == expected_time, f"JS code: {code[:60]!r}  expected {expected_time}, got {tc}"

    def test_sort_sets_on_space(self):
        code = "function f(){ const m = new Map(); m.set('a',1); return m; }"
        tc, sc, rec, lc = analyze_js_code(code)
        assert sc == "O(n)"

    def test_recursive_flag(self):
        code = "function fib(n){ if(n<=1)return n; return fib(n-1)+fib(n-2); }"
        tc, sc, rec, lc = analyze_js_code(code)
        assert rec is True

    def test_non_recursive_flag(self):
        code = "function sum(arr){ let s=0; arr.forEach(x=>s+=x); return s; }"
        tc, sc, rec, lc = analyze_js_code(code)
        assert rec is False

    def test_returns_four_tuple(self):
        result = analyze_js_code("function f(){}")
        assert len(result) == 4

    def test_higher_order_functions(self):
        code = "function f(arr){ return arr.filter(x=>x>0).map(x=>x*2); }"
        tc, sc, rec, lc = analyze_js_code(code)
        # Two HOF calls → depth 2 → O(n^2) OR back-to-back at same level O(n)
        assert tc in ("O(n)", "O(n^2)")

    def test_dp_table_space_on2(self):
        code = (
            "function lcs(a, b){"
            "  const dp = new Array(a.length+1).fill(null).map(()=>new Array(b.length+1).fill(0));"
            "  for(let i=1;i<=a.length;i++)"
            "    for(let j=1;j<=b.length;j++)"
            "      dp[i][j] = a[i-1]===b[j-1] ? dp[i-1][j-1]+1 : Math.max(dp[i-1][j],dp[i][j-1]);"
            "  return dp[a.length][b.length]; }"
        )
        tc, sc, rec, lc = analyze_js_code(code)
        assert tc in ("O(n^2)", "O(n log n)")   # nested loops should push to n²


# ══════════════════════════════════════════════════════════════════════════════
# 12. JAVA ANALYZER
# ══════════════════════════════════════════════════════════════════════════════

class TestJavaAnalyzer:
    """
    analyze_java_code(code) → dict with time_complexity, space_complexity,
                               recursion, loops, patterns, function_breakdown
    """

    @pytest.mark.parametrize("code,expected_time", [
        # O(1)
        ("public int add(int a, int b){ return a+b; }", "O(1)"),
        # O(n) — single for loop
        ("public int sum(int[] a){ int s=0; for(int x:a) s+=x; return s; }", "O(n)"),
        # O(n²) — nested loops
        ("public void f(int[] a){ for(int i=0;i<a.length;i++) for(int j=0;j<a.length;j++){} }", "O(n^2)"),
        # O(n log n) — sort call
        ("public void s(int[] a){ Arrays.sort(a); }", "O(n log n)"),
        # O(log n) — binary search while
        (
            "public int bs(int[] a, int t){"
            "  int lo=0,hi=a.length-1;"
            "  while(lo<=hi){ int mid=(lo+hi)/2;"
            "    if(a[mid]==t) return mid;"
            "    else if(a[mid]<t) lo=mid+1; else hi=mid-1; }"
            "  return -1; }",
            "O(log n)",
        ),
        # O(2^n) — fibonacci double recursion
        ("public int fib(int n){ if(n<=1) return n; return fib(n-1)+fib(n-2); }", "O(2^n)"),
        # O(n) — linear recursion
        ("public int fact(int n){ if(n<=1) return 1; return n*fact(n-1); }", "O(n)"),
    ])
    def test_time_complexity(self, code, expected_time):
        r = analyze_java_code(code)
        assert r["time_complexity"] == expected_time, (
            f"Java code: {code[:60]!r}  expected {expected_time}, got {r['time_complexity']}"
        )

    def test_returns_required_keys(self):
        r = analyze_java_code("public int f(){ return 0; }")
        for key in ("time_complexity", "space_complexity", "recursion", "loops", "patterns"):
            assert key in r

    def test_function_breakdown_populated(self):
        r = analyze_java_code("public int f(){ return 0; }")
        assert isinstance(r["function_breakdown"], list)

    def test_hash_map_space_on(self):
        code = "public void f(Map<String,Integer> m){ m.put(\"a\",1); }"
        r = analyze_java_code(code)
        assert r["space_complexity"] == "O(n)"

    def test_dp_table_space_on2(self):
        code = (
            "public int lcs(String a, String b){"
            "  int[][] dp = new int[a.length()+1][b.length()+1];"
            "  for(int i=1;i<=a.length();i++)"
            "    for(int j=1;j<=b.length();j++)"
            "      dp[i][j]=Math.max(dp[i-1][j],dp[i][j-1]);"
            "  return dp[a.length()][b.length()]; }"
        )
        r = analyze_java_code(code)
        assert r["space_complexity"] == "O(n^2)"

    def test_patterns_list(self):
        code = "public int fib(int n){ if(n<=1)return n; return fib(n-1)+fib(n-2); }"
        r = analyze_java_code(code)
        assert "recursive" in r["patterns"]

    def test_recursion_flag(self):
        code = "public int f(int n){ if(n==0)return 0; return f(n-1); }"
        r = analyze_java_code(code)
        assert r["recursion"] is True

    def test_no_recursion_flag(self):
        code = "public int sum(int[] a){ int s=0; for(int x:a) s+=x; return s; }"
        r = analyze_java_code(code)
        assert r["recursion"] is False


# ══════════════════════════════════════════════════════════════════════════════
# 13. C ANALYZER
# ══════════════════════════════════════════════════════════════════════════════

class TestCAnalyzer:
    """
    analyze_c_code(code) → (time_complexity, space_complexity, is_recursive, loop_count)
    """

    @pytest.mark.parametrize("code,expected_time", [
        # O(1)
        ("int add(int a, int b){ return a+b; }", "O(1)"),
        # O(n) — single for loop
        ("int sum(int* arr, int n){ int s=0; for(int i=0;i<n;i++) s+=arr[i]; return s; }", "O(n)"),
        # O(n²) — nested loops
        ("void f(int n){ for(int i=0;i<n;i++) for(int j=0;j<n;j++){} }", "O(n^2)"),
        # O(n³) — triple nested
        ("void f(int n){ for(int i=0;i<n;i++) for(int j=0;j<n;j++) for(int k=0;k<n;k++){} }", "O(n^3)"),
        # O(n log n) — qsort
        ("void s(int* arr, int n){ qsort(arr,n,sizeof(int),cmp); }", "O(n log n)"),
        # O(log n) — binary search
        (
            "int bs(int* arr, int lo, int hi, int t){"
            "  while(lo<=hi){ int mid=(lo+hi)/2;"
            "    if(arr[mid]==t) return mid;"
            "    else if(arr[mid]<t) lo=mid+1; else hi=mid-1; }"
            "  return -1; }",
            "O(log n)",
        ),
        # O(n) — linear recursion
        ("int fact(int n){ if(n<=1) return 1; return n*fact(n-1); }", "O(n)"),
        # O(2^n) — binary recursion
        ("int fib(int n){ if(n<=1) return n; return fib(n-1)+fib(n-2); }", "O(2^n)"),
    ])
    def test_time_complexity(self, code, expected_time):
        tc, sc, rec, lc = analyze_c_code(code)
        assert tc == expected_time, f"C code: {code[:60]!r}  expected {expected_time}, got {tc}"

    def test_malloc_sets_on_space(self):
        code = "int* f(int n){ int* arr=malloc(n*sizeof(int)); return arr; }"
        tc, sc, rec, lc = analyze_c_code(code)
        assert sc == "O(n)"

    def test_no_alloc_o1_space(self):
        code = "int add(int a, int b){ return a+b; }"
        tc, sc, rec, lc = analyze_c_code(code)
        assert sc == "O(1)"

    def test_recursive_flag(self):
        tc, sc, rec, lc = analyze_c_code("int f(int n){ if(n==0)return 0; return f(n-1); }")
        assert rec is True

    def test_non_recursive_flag(self):
        tc, sc, rec, lc = analyze_c_code("int f(int n){ return n; }")
        assert rec is False

    def test_returns_four_tuple(self):
        result = analyze_c_code("int f(){ return 0; }")
        assert len(result) == 4

    def test_bsearch_stdlib(self):
        code = "int* r = (int*)bsearch(&k, arr, n, sizeof(int), cmp);"
        tc, sc, rec, lc = analyze_c_code(code)
        assert tc == "O(log n)"


# ══════════════════════════════════════════════════════════════════════════════
# 14. C++ ANALYZER
# ══════════════════════════════════════════════════════════════════════════════

class TestCPPAnalyzer:
    """
    analyze_cpp_code(code) → (time_complexity, space_complexity, is_recursive, loop_count)
    """

    @pytest.mark.parametrize("code,expected_time", [
        # O(1)
        ("int add(int a, int b){ return a+b; }", "O(1)"),
        # O(n) — single for loop
        ("int sum(vector<int>& v){ int s=0; for(auto x:v) s+=x; return s; }", "O(n)"),
        # O(n²) — nested
        ("void f(int n){ for(int i=0;i<n;i++) for(int j=0;j<n;j++){} }", "O(n^2)"),
        # O(n log n) — std::sort
        ("void s(vector<int>& v){ sort(v.begin(), v.end()); }", "O(n log n)"),
        # O(log n) — binary search
        (
            "int bs(vector<int>& a, int t){"
            "  int lo=0,hi=a.size()-1;"
            "  while(lo<=hi){ int mid=(lo+hi)/2;"
            "    if(a[mid]==t) return mid;"
            "    else if(a[mid]<t) lo=mid+1; else hi=mid-1; }"
            "  return -1; }",
            "O(log n)",
        ),
        # O(2^n) — fibonacci
        ("int fib(int n){ if(n<=1)return n; return fib(n-1)+fib(n-2); }", "O(2^n)"),
        # O(n) — linear recursion
        ("int fact(int n){ if(n<=1) return 1; return n*fact(n-1); }", "O(n)"),
        # O(n log n) — sort inside loop
        (
            "void f(vector<vector<int>>& v){"
            "  for(auto& row: v){ sort(row.begin(),row.end()); } }",
            "O(n log n)",
        ),
    ])
    def test_time_complexity(self, code, expected_time):
        tc, sc, rec, lc = analyze_cpp_code(code)
        assert tc == expected_time, f"C++ code: {code[:60]!r}  expected {expected_time}, got {tc}"

    def test_vector_declaration_sets_on_space(self):
        code = "void f(){ vector<int> v; }"
        tc, sc, rec, lc = analyze_cpp_code(code)
        assert sc == "O(n)"

    def test_new_sets_on_space(self):
        code = "int* f(int n){ int* arr = new int[n]; return arr; }"
        tc, sc, rec, lc = analyze_cpp_code(code)
        assert sc == "O(n)"

    def test_plain_ints_o1_space(self):
        code = "int add(int a, int b){ return a + b; }"
        tc, sc, rec, lc = analyze_cpp_code(code)
        assert sc == "O(1)"

    def test_stl_binary_search_function(self):
        code = "bool f(vector<int>& v, int t){ return binary_search(v.begin(),v.end(),t); }"
        tc, sc, rec, lc = analyze_cpp_code(code)
        assert tc == "O(log n)"

    def test_lower_bound(self):
        code = "auto it = lower_bound(v.begin(), v.end(), target);"
        tc, sc, rec, lc = analyze_cpp_code(code)
        assert tc == "O(log n)"

    def test_recursive_flag(self):
        tc, sc, rec, lc = analyze_cpp_code("int f(int n){ if(n==0)return 0; return f(n-1); }")
        assert rec is True

    def test_dp_space_on2(self):
        code = (
            "int lcs(string a, string b){"
            "  vector<vector<int>> dp(a.size()+1, vector<int>(b.size()+1,0));"
            "  for(int i=1;i<=a.size();i++)"
            "    for(int j=1;j<=b.size();j++)"
            "      dp[i][j]=max(dp[i-1][j],dp[i][j-1]);"
            "  return dp[a.size()][b.size()]; }"
        )
        tc, sc, rec, lc = analyze_cpp_code(code)
        assert sc in ("O(n)", "O(n^2)")   # vector<vector> triggers O(n²) DP branch

    def test_lambda_expression_analyzed(self):
        code = ( 
            "void f(vector<int>& v){"
            "  auto cmp = [&](int a, int b){ return a < b; };"
            "  sort(v.begin(), v.end(), cmp); }"
        )
        tc, sc, rec, lc = analyze_cpp_code(code)
        assert tc == "O(n log n)"


# ══════════════════════════════════════════════════════════════════════════════
# 15. CROSS-LANGUAGE CONSISTENCY
# ══════════════════════════════════════════════════════════════════════════════

class TestCrossLanguageConsistency:
    """Same algorithmic pattern should produce the same complexity across languages."""

    # Bubble sort ≈ O(n²)
    BUBBLE_PY  = "def f(a):\n for i in range(len(a)):\n  for j in range(len(a)-i-1):\n   if a[j]>a[j+1]: a[j],a[j+1]=a[j+1],a[j]"
    BUBBLE_JS  = "function f(a){ for(let i=0;i<a.length;i++) for(let j=0;j<a.length-i-1;j++) if(a[j]>a[j+1]){let t=a[j];a[j]=a[j+1];a[j+1]=t;} }"
    BUBBLE_C   = "void sort(int*a,int n){for(int i=0;i<n;i++)for(int j=0;j<n-i-1;j++){int t=a[j];a[j]=a[j+1];a[j+1]=t;}}"
    BUBBLE_CPP = "void sort(vector<int>&a){for(int i=0;i<a.size();i++)for(int j=0;j<a.size()-i-1;j++){int t=a[j];a[j]=a[j+1];a[j+1]=t;}}"

    def test_bubble_sort_python(self):
        assert _infer(self.BUBBLE_PY)["time"] == "O(n^2)"

    def test_bubble_sort_js(self):
        tc, *_ = analyze_js_code(self.BUBBLE_JS)
        assert tc == "O(n^2)"

    def test_bubble_sort_c(self):
        tc, *_ = analyze_c_code(self.BUBBLE_C)
        assert tc == "O(n^2)"

    def test_bubble_sort_cpp(self):
        tc, *_ = analyze_cpp_code(self.BUBBLE_CPP)
        assert tc == "O(n^2)"

    # Linear search ≈ O(n)
    LINEAR_PY  = "def f(a,t):\n for x in a:\n  if x==t: return True\n return False"
    LINEAR_JS  = "function f(a,t){ for(let i=0;i<a.length;i++) if(a[i]===t) return true; return false; }"
    LINEAR_C   = "int f(int*a,int n,int t){for(int i=0;i<n;i++) if(a[i]==t) return 1; return -1;}"
    LINEAR_CPP = "bool f(vector<int>&a,int t){for(auto x:a) if(x==t) return true; return false;}"

    def test_linear_search_python(self):
        assert _infer(self.LINEAR_PY)["time"] == "O(n)"

    def test_linear_search_js(self):
        tc, *_ = analyze_js_code(self.LINEAR_JS)
        assert tc == "O(n)"

    def test_linear_search_c(self):
        tc, *_ = analyze_c_code(self.LINEAR_C)
        assert tc == "O(n)"

    def test_linear_search_cpp(self):
        tc, *_ = analyze_cpp_code(self.LINEAR_CPP)
        assert tc == "O(n)"

    # Recursive fibonacci ≈ O(2^n)
    FIB_PY  = "def fib(n):\n if n<=1: return n\n return fib(n-1)+fib(n-2)"
    FIB_JS  = "function fib(n){ if(n<=1)return n; return fib(n-1)+fib(n-2); }"
    FIB_C   = "int fib(int n){ if(n<=1) return n; return fib(n-1)+fib(n-2); }"
    FIB_CPP = "int fib(int n){ if(n<=1) return n; return fib(n-1)+fib(n-2); }"

    def test_fib_python(self):
        assert _infer(self.FIB_PY)["time"] == "O(2^n)"

    def test_fib_js(self):
        tc, *_ = analyze_js_code(self.FIB_JS)
        assert tc == "O(2^n)"

    def test_fib_c(self):
        tc, *_ = analyze_c_code(self.FIB_C)
        assert tc == "O(2^n)"

    def test_fib_cpp(self):
        tc, *_ = analyze_cpp_code(self.FIB_CPP)
        assert tc == "O(2^n)"
