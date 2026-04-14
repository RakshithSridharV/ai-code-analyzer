import pytest
from app import app
from analyzer.pattern_detector import detect_patterns
from analyzer.feature_extractor import extract_features
from analyzer.quality_score import calculate_quality_score
from analyzer.language_detector import detect_language

# -------------------------
# ORIGINAL TESTS (Fixed logic)
# -------------------------
def test_nested_loop_detection():
    patterns = detect_patterns("O(n^2)", "O(1)", False)
    assert "nested_loop" in patterns
    assert "efficient_code" not in patterns

def test_efficient_code_detection():
    patterns = detect_patterns("O(n)", "O(1)", False)
    assert "efficient_code" in patterns

def test_feature_extraction_length():
    patterns = ["nested_loop", "extra_memory"]
    features = extract_features("O(n^2)", "O(n)", patterns)
    assert len(features) == 5

def test_quality_score_range():
    ai_prediction = {"label": "Inefficient", "confidence": 0.85}
    features = [2, 0, 1, 3, 2]
    score = calculate_quality_score(ai_prediction, features)
    assert 0 <= score <= 100

# -------------------------
# LANGUAGE DETECTOR TESTS
# -------------------------
def test_language_detector_python():
    assert detect_language("def hello():\n    pass") == "python"

def test_language_detector_javascript():
    assert detect_language("function hello() {}") == "javascript"

def test_language_detector_java():
    assert detect_language("public class Test {}") == "java"

def test_language_detector_c():
    assert detect_language("int main() { return 0; }") == "c"

def test_language_detector_cpp_unsupported():
    assert detect_language("#include <iostream>\nint main() { std::cout << 1; }") == "cpp_unsupported"

# -------------------------
# ENDPOINT TESTS
# -------------------------
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_analyze_python_valid(client):
    res = client.post("/analyze", json={
        "language": "python",
        "code": "def test():\n    for i in range(10):\n        print(i)"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["language"] == "python"
    assert "time_complexity" in data["analysis"]
    assert "ai" in data
    assert "quality_score" in data

def test_analyze_empty_code(client):
    """Empty code is valid Python (ast.parse succeeds). Should return O(1) analysis."""
    res = client.post("/analyze", json={"language": "python", "code": ""})
    assert res.status_code == 200
    data = res.get_json()
    assert data["analysis"]["time_complexity"] == "O(1)"

def test_analyze_unsupported_cpp(client):
    res = client.post("/analyze", json={
        "language": "auto",
        "code": "#include <iostream>\nint main() { std::cout << 1; }"
    })
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data
    assert "Real C++" in data["error"]

def test_analyze_too_large(client):
    res = client.post("/analyze", json={
        "language": "python",
        "code": "A" * 10001
    })
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data
    assert "too large" in data["error"]

def test_analyze_syntax_error(client):
    res = client.post("/analyze", json={
        "language": "python",
        "code": "def def def syntax error"
    })
    # Just verify it doesn't crash 500
    assert res.status_code == 200
    assert "error" in res.get_json()


# -------------------------
# LANGUAGE DETECTOR EDGE CASES
# -------------------------
def test_language_detector_python_with_class():
    """Python code with 'class' keyword should NOT be detected as Java."""
    code = "class MyClass:\n    def __init__(self):\n        self.x = 1"
    assert detect_language(code) == "python"


def test_language_detector_js_with_int_comment():
    """JS code mentioning 'int' in a comment should NOT be detected as C."""
    code = "function add(a, b) {\n    // int is not a keyword in JS\n    return a + b;\n}"
    assert detect_language(code) == "javascript"

# -------------------------
# NEW ANALYSIS ENGINE TESTS
# -------------------------
import ast
from analyzer.cyclomatic_analyzer import CyclomaticAnalyzer
from analyzer.confidence_estimator import ConfidenceEstimator

def test_cyclomatic_simple():
    code = "def foo(x):\n    return x + 1"
    tree = ast.parse(code)
    analyzer = CyclomaticAnalyzer(tree, code)
    res = analyzer.analyze()
    assert res["score"] == 1

def test_cyclomatic_if():
    code = "def foo(x):\n    if x > 0:\n        return x\n    return -x"
    tree = ast.parse(code)
    analyzer = CyclomaticAnalyzer(tree, code)
    res = analyzer.analyze()
    assert res["score"] == 2

def test_cyclomatic_nested():
    code = "def foo():\n    for i in range(10):\n        if i > 5:\n            if i == 8:\n                pass"
    tree = ast.parse(code)
    analyzer = CyclomaticAnalyzer(tree, code)
    res = analyzer.analyze()
    assert res["score"] == 4

def test_cyclomatic_boolop():
    code = "def foo(a, b, c):\n    if a and b and c:\n        return True"
    tree = ast.parse(code)
    analyzer = CyclomaticAnalyzer(tree, code)
    res = analyzer.analyze()
    # if +1, and +2 -> D=3. Score = 3+1 = 4.
    assert res["score"] == 4

def test_cyclomatic_risk_low():
    tree = ast.parse("def f(): pass")
    analyzer = CyclomaticAnalyzer(tree, "def f(): pass")
    l, r = analyzer._risk_label(3)
    assert r == "low"

def test_cyclomatic_risk_high():
    tree = ast.parse("def f(): pass")
    analyzer = CyclomaticAnalyzer(tree, "def f(): pass")
    l, r = analyzer._risk_label(9)
    assert r == "high"

def test_confidence_high():
    code = "for i in range(10):\n    pass"
    tree = ast.parse(code)
    estimator = ConfidenceEstimator(tree, code, {"time": "O(n)", "space": "O(1)"})
    res = estimator.estimate()
    assert res["time_confidence"] >= 0.85

def test_confidence_reduced_call():
    code = "for x in get_data():\n    pass"
    tree = ast.parse(code)
    estimator = ConfidenceEstimator(tree, code, {"time": "O(n)", "space": "O(1)"})
    res = estimator.estimate()
    assert res["time_confidence"] <= 0.85

def test_confidence_alternative_n2():
    # Adding a return to ensure confidence < 0.85 since 1.0 - 0.15 = 0.85
    code = "for x in get_data():\n    return x"
    tree = ast.parse(code)
    estimator = ConfidenceEstimator(tree, code, {"time": "O(n^2)", "space": "O(1)"})
    res = estimator.estimate()
    assert res["time_alternative"] == "O(n log n)"

def test_confidence_no_alternative_high():
    code = "for i in range(10):\n    pass"
    tree = ast.parse(code)
    estimator = ConfidenceEstimator(tree, code, {"time": "O(n^2)", "space": "O(1)"})
    res = estimator.estimate()
    assert res["time_alternative"] is None