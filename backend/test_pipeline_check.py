import sys, ast
sys.path.insert(0, '.')

errors = []

# ── 1. Python full analyze() pipeline ─────────────────────────────────────────
try:
    from analyzer.parser import parse_code
    from analyzer.recursion_detector import detect_recursion
    from analyzer.time_complexity import estimate_time_complexity
    from analyzer.space_complexity import estimate_space_complexity
    from analyzer.pattern_detector import detect_patterns
    from analyzer.feature_extractor import extract_features
    from analyzer.ai_predictor import predict_code_quality
    from analyzer.optimization_ranker import rank_optimizations
    from analyzer.explanations import get_detailed_explanation
    from analyzer.quality_score import calculate_quality_score
    from analyzer.code_optimizer import get_optimized_code
    from analyzer.eco_score import calculate_eco_score
    from analyzer.suggestions import get_suggestions
    from analyzer.function_splitter import analyze_functions

    code = (
        "def bubble_sort(arr):\n"
        "    for i in range(len(arr)):\n"
        "        for j in range(len(arr) - i - 1):\n"
        "            if arr[j] > arr[j+1]:\n"
        "                arr[j], arr[j+1] = arr[j+1], arr[j]\n"
        "    return arr\n"
    )

    tree = parse_code(code)
    assert not isinstance(tree, str), "Parse error: " + str(tree)

    is_recursive = detect_recursion(tree)
    time_c = "O(2^n)" if is_recursive else estimate_time_complexity(tree)
    space_c = estimate_space_complexity(code, is_recursive)
    patterns = detect_patterns(time_c, space_c, is_recursive)
    features = extract_features(time_c, space_c, patterns)
    ai_pred = predict_code_quality(features)
    rank_optimizations(patterns, ai_pred)
    get_detailed_explanation(patterns, time_c, space_c)
    qs = calculate_quality_score(ai_pred, features)
    get_optimized_code(patterns, time_c, "python")
    eco = calculate_eco_score(time_c, space_c, "python")
    sugg = get_suggestions(patterns)
    funcs = analyze_functions(code)

    eco_val = eco.get("eco_score_100") if isinstance(eco, dict) else None
    print("Python pipeline:  time=%s  space=%s  recursive=%s  quality=%s  eco=%s  functions=%d  suggestions=%d  PASS"
          % (time_c, space_c, is_recursive, qs, eco_val, len(funcs), len(sugg)))

except Exception as e:
    errors.append("Python pipeline FAIL: " + str(e))
    import traceback; traceback.print_exc()


# ── 2. InferenceEngine ────────────────────────────────────────────────────────
try:
    from analyzer.inference_engine import InferenceEngine

    code_n2 = "def foo(arr):\n    for i in arr:\n        for j in arr:\n            pass"
    tree = ast.parse(code_n2)
    ie = InferenceEngine(tree, code_n2).analyze()
    assert ie["time"] == "O(n^2)", "Expected O(n^2), got " + ie["time"]
    assert ie["space"] == "O(1)",  "Expected O(1), got " + ie["space"]

    code_n = "def bar(arr):\n    for x in arr:\n        pass"
    ie2 = InferenceEngine(ast.parse(code_n), code_n).analyze()
    assert ie2["time"] == "O(n)", "Expected O(n), got " + ie2["time"]

    tree3 = ast.parse("")
    ie3 = InferenceEngine(tree3, "").analyze()
    assert ie3["time"] == "O(1)", "Expected O(1) for empty, got " + ie3["time"]

    code_space = "def baz(arr):\n    result = []\n    for x in arr:\n        result.append(x)\n    return result"
    ie4 = InferenceEngine(ast.parse(code_space), code_space).analyze()
    assert ie4["space"] == "O(n)", "Expected O(n) space, got " + ie4["space"]

    print("InferenceEngine:  time=%s  space=%s  PASS" % (ie["time"], ie["space"]))
except Exception as e:
    errors.append("InferenceEngine FAIL: " + str(e))
    import traceback; traceback.print_exc()


# ── 3. ExplanationBuilder ────────────────────────────────────────────────────
try:
    from analyzer.explanation_builder import ExplanationBuilder
    from analyzer.inference_engine import InferenceEngine

    code_n2 = "def foo(arr):\n    for i in arr:\n        for j in arr:\n            pass"
    tree = ast.parse(code_n2)
    ie_result = InferenceEngine(tree, code_n2).analyze()
    eb = ExplanationBuilder(ie_result, code_n2, "foo").build()
    assert isinstance(eb, str) and len(eb) > 10, "Expected non-empty string"
    assert "foo" in eb, "Expected fn name in explanation"

    ie2 = InferenceEngine(ast.parse(""), "").analyze()
    eb2 = ExplanationBuilder(ie2, "", "bar").build()
    assert "constant time" in eb2, "Expected 'constant time': " + eb2

    print("ExplanationBuilder:  result='%s...'  PASS" % eb[:60])
except Exception as e:
    errors.append("ExplanationBuilder FAIL: " + str(e))
    import traceback; traceback.print_exc()


# ── 4. DataFlowTracer ───────────────────────────────────────────────────────
try:
    from analyzer.data_flow_tracer import DataFlowTracer

    code1 = "items = [1, 2, 3]\nif x in items:\n    pass"
    f1 = DataFlowTracer(ast.parse(code1), code1).trace()
    assert any(f["pattern"] == "list_membership" for f in f1), "Missing list_membership: " + str(f1)

    code2 = "s = ''\nfor x in arr:\n    s += x"
    f2 = DataFlowTracer(ast.parse(code2), code2).trace()
    assert any(f["pattern"] == "string_concat_loop" for f in f2), "Missing string_concat_loop: " + str(f2)

    code3 = "for i in range(10):\n    n = len(arr)"
    f3 = DataFlowTracer(ast.parse(code3), code3).trace()
    assert any(f["pattern"] == "len_in_loop" for f in f3), "Missing len_in_loop: " + str(f3)

    code5 = "matrix = [[i*j for j in row] for row in grid]"
    f5 = DataFlowTracer(ast.parse(code5), code5).trace()
    assert any(f["pattern"] == "nested_listcomp" for f in f5), "Missing nested_listcomp: " + str(f5)

    print("DataFlowTracer:  findings=%d  PASS" % len(f1 + f2 + f3 + f5))
except Exception as e:
    errors.append("DataFlowTracer FAIL: " + str(e))
    import traceback; traceback.print_exc()


# ── 5. RecursionClassifier ───────────────────────────────────────────────────
try:
    from analyzer.recursion_classifier import RecursionClassifier

    tree = ast.parse("def fib(n):\n    if n<=1: return n\n    return fib(n-1)+fib(n-2)")
    r = RecursionClassifier(tree, "").classify()
    assert r["is_recursive"] == True,  "Expected is_recursive=True"
    assert r["pattern"] == "binary",   "Expected pattern=binary"
    assert "O(2^n)" in r["complexity_hint"], "Expected O(2^n) hint"

    tree2 = ast.parse("def fact(n):\n    if n==0: return 1\n    return n*fact(n-1)")
    r2 = RecursionClassifier(tree2, "").classify()
    assert r2["pattern"] == "linear", "Expected pattern=linear"

    tree3 = ast.parse("from functools import lru_cache\n@lru_cache\ndef fib(n):\n    if n<=1: return n\n    return fib(n-1)+fib(n-2)")
    r3 = RecursionClassifier(tree3, "").classify()
    assert r3["is_memoized"] == True, "Expected is_memoized=True"

    print("RecursionClassifier:  pattern=%s  hint=%s  PASS" % (r["pattern"], r["complexity_hint"]))
except Exception as e:
    errors.append("RecursionClassifier FAIL: " + str(e))
    import traceback; traceback.print_exc()


# ── 6. AntiPatternDetector ───────────────────────────────────────────────────
try:
    from analyzer.anti_pattern_detector import AntiPatternDetector

    code = "def foo(x=[]):\n    pass\ntry:\n    pass\nexcept:\n    pass"
    ap = AntiPatternDetector(ast.parse(code), code).detect()
    assert any(f["pattern"] == "bare_except" for f in ap), "Missing bare_except"
    assert any(f["pattern"] == "mutable_default_arg" for f in ap), "Missing mutable_default_arg"

    code2 = "counter = 0\ndef inc():\n    global counter\n    counter += 1"
    ap2 = AntiPatternDetector(ast.parse(code2), code2).detect()
    assert any(f["pattern"] == "global_modification" for f in ap2), "Missing global_modification"

    code3 = "for x in arr:\n    return x"
    ap3 = AntiPatternDetector(ast.parse(code3), code3).detect()
    assert any(f["pattern"] == "return_in_loop" for f in ap3), "Missing return_in_loop"

    print("AntiPatternDetector:  findings=%d  PASS" % len(ap))
except Exception as e:
    errors.append("AntiPatternDetector FAIL: " + str(e))
    import traceback; traceback.print_exc()


# ── 7. JavaScript pipeline ───────────────────────────────────────────────────
try:
    from analyzer.js_analyzer import analyze_js_code
    js = "function sum(arr) { let s=0; for(let i=0;i<arr.length;i++) s+=arr[i]; return s; }"
    tc, sc, rec, loops = analyze_js_code(js)
    print("JS pipeline:  time=%s  space=%s  recursive=%s  PASS" % (tc, sc, rec))
except Exception as e:
    errors.append("JS pipeline FAIL: " + str(e))
    import traceback; traceback.print_exc()


# ── 8. Java pipeline ─────────────────────────────────────────────────────────
try:
    from analyzer.java_analyzer import analyze_java_code
    java = "public class Main { public static int sum(int[] arr) { int s=0; for(int x : arr) s+=x; return s; } }"
    r = analyze_java_code(java)
    print("Java pipeline:  time=%s  space=%s  PASS" % (r["time_complexity"], r["space_complexity"]))
except Exception as e:
    errors.append("Java pipeline FAIL: " + str(e))
    import traceback; traceback.print_exc()


# ── 9. C pipeline ─────────────────────────────────────────────────────────────
try:
    from analyzer.c_analyzer import analyze_c_code
    c = "int main() { for(int i=0;i<n;i++) printf(\"%d\",i); return 0; }"
    tc, sc, rec, loops = analyze_c_code(c)
    print("C pipeline:  time=%s  space=%s  PASS" % (tc, sc))
except Exception as e:
    errors.append("C pipeline FAIL: " + str(e))
    import traceback; traceback.print_exc()


# ── 10. Language detector ─────────────────────────────────────────────────────
try:
    from analyzer.language_detector import detect_language
    assert detect_language("def foo(): pass") == "python"
    assert detect_language("function foo() {}") == "javascript"
    assert detect_language("public class A {}") == "java"
    print("language_detector:  python/js/java  PASS")
except Exception as e:
    errors.append("language_detector FAIL: " + str(e))
    import traceback; traceback.print_exc()


# ── 11. Database ──────────────────────────────────────────────────────────────
try:
    from database import init_db, save_analysis, get_history, code_hash
    init_db()
    h = code_hash("test code")
    assert isinstance(h, str) and len(h) > 0, "code_hash returned empty"
    rows = get_history(5, user_id=None)
    assert isinstance(rows, list), "get_history should return a list"
    print("database:  hash=%s  history_rows=%d  PASS" % (h[:8] + "...", len(rows)))
except Exception as e:
    errors.append("database FAIL: " + str(e))
    import traceback; traceback.print_exc()


# ── Summary ───────────────────────────────────────────────────────────────────
print()
if errors:
    print("=" * 50)
    print("FAILURES (%d):" % len(errors))
    for err in errors:
        print("  " + err)
    sys.exit(1)
else:
    print("=" * 50)
    print("ALL CHECKS PASSED (11/11)")
    sys.exit(0)
