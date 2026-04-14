import sys, ast
sys.path.insert(0, '.')

errors = []

# ── Engine 4: RecursionClassifier ──────────────────────────────────────────
try:
    from analyzer.recursion_classifier import RecursionClassifier

    # Binary recursion (fib)
    tree = ast.parse("def fib(n):\n    if n<=1: return n\n    return fib(n-1)+fib(n-2)")
    r = RecursionClassifier(tree, '').classify()
    assert r['is_recursive'] == True,        f"Expected is_recursive=True, got {r}"
    assert r['pattern'] == 'binary',         f"Expected pattern=binary, got {r['pattern']}"
    assert 'O(2^n)' in r['complexity_hint'], f"Expected O(2^n) hint, got {r['complexity_hint']}"

    # Linear recursion (factorial)
    tree2 = ast.parse("def fact(n):\n    if n==0: return 1\n    return n*fact(n-1)")
    r2 = RecursionClassifier(tree2, '').classify()
    assert r2['pattern'] == 'linear',  f"Expected pattern=linear, got {r2['pattern']}"

    # Memoized
    tree3 = ast.parse("from functools import lru_cache\n@lru_cache\ndef fib(n):\n    if n<=1: return n\n    return fib(n-1)+fib(n-2)")
    r3 = RecursionClassifier(tree3, '').classify()
    assert r3['is_memoized'] == True,  f"Expected is_memoized=True"

    print("RecursionClassifier  OK  pattern=%s hint=%s" % (r['pattern'], r['complexity_hint']))
except Exception as e:
    errors.append(f"RecursionClassifier FAIL: {e}")
    print(f"RecursionClassifier FAIL: {e}")

# ── Engine 1: InferenceEngine ───────────────────────────────────────────────
try:
    from analyzer.inference_engine import InferenceEngine

    # Nested loops -> O(n^2)
    code_n2 = "def foo(arr):\n    for i in arr:\n        for j in arr:\n            pass"
    tree = ast.parse(code_n2)
    ie = InferenceEngine(tree, code_n2).analyze()
    assert ie['time'] == 'O(n^2)', f"Expected O(n^2), got {ie['time']}"
    assert ie['space'] == 'O(1)',  f"Expected O(1) space, got {ie['space']}"

    # Single loop -> O(n)
    code_n = "def bar(arr):\n    for x in arr:\n        pass"
    tree2 = ast.parse(code_n)
    ie2 = InferenceEngine(tree2, code_n).analyze()
    assert ie2['time'] == 'O(n)',  f"Expected O(n), got {ie2['time']}"

    # Empty code -> O(1)
    tree3 = ast.parse("")
    ie3 = InferenceEngine(tree3, "").analyze()
    assert ie3['time'] == 'O(1)', f"Expected O(1) for empty, got {ie3['time']}"

    # List with append in loop -> O(n) space
    code_space = "def baz(arr):\n    result = []\n    for x in arr:\n        result.append(x)\n    return result"
    tree4 = ast.parse(code_space)
    ie4 = InferenceEngine(tree4, code_space).analyze()
    assert ie4['space'] == 'O(n)', f"Expected O(n) space for append-in-loop, got {ie4['space']}"

    print("InferenceEngine      OK  time=%s space=%s" % (ie['time'], ie['space']))
except Exception as e:
    errors.append(f"InferenceEngine FAIL: {e}")
    print(f"InferenceEngine FAIL: {e}")

# ── Engine 2: ExplanationBuilder ────────────────────────────────────────────
try:
    from analyzer.explanation_builder import ExplanationBuilder

    code_n2 = "def foo(arr):\n    for i in arr:\n        for j in arr:\n            pass"
    tree = ast.parse(code_n2)
    ie_result = InferenceEngine(tree, code_n2).analyze()
    eb = ExplanationBuilder(ie_result, code_n2, 'foo').build()
    assert isinstance(eb, str), "Expected string"
    assert len(eb) > 10,       "Expected non-empty string"
    assert 'foo' in eb,        f"Expected fn name in explanation: {eb}"

    # O(1) path
    tree2 = ast.parse("")
    ie2 = InferenceEngine(tree2, "").analyze()
    eb2 = ExplanationBuilder(ie2, "", 'bar').build()
    assert 'constant time' in eb2, f"Expected 'constant time': {eb2}"

    print("ExplanationBuilder   OK  result=%s..." % eb[:50])
except Exception as e:
    errors.append(f"ExplanationBuilder FAIL: {e}")
    print(f"ExplanationBuilder FAIL: {e}")

# ── Engine 3: DataFlowTracer ─────────────────────────────────────────────────
try:
    from analyzer.data_flow_tracer import DataFlowTracer

    # Pattern 1: list membership
    code1 = "items = [1, 2, 3]\nif x in items:\n    pass"
    tree1 = ast.parse(code1)
    findings1 = DataFlowTracer(tree1, code1).trace()
    assert any(f['pattern'] == 'list_membership' for f in findings1), \
        f"Missing list_membership finding: {findings1}"

    # Pattern 2: string concat in loop
    code2 = "s = ''\nfor x in arr:\n    s += x"
    tree2 = ast.parse(code2)
    findings2 = DataFlowTracer(tree2, code2).trace()
    assert any(f['pattern'] == 'string_concat_loop' for f in findings2), \
        f"Missing string_concat_loop finding: {findings2}"

    # Pattern 3: len in loop
    code3 = "for i in range(10):\n    n = len(arr)"
    tree3 = ast.parse(code3)
    findings3 = DataFlowTracer(tree3, code3).trace()
    assert any(f['pattern'] == 'len_in_loop' for f in findings3), \
        f"Missing len_in_loop finding: {findings3}"

    # Pattern 5: nested listcomp
    code5 = "matrix = [[i*j for j in row] for row in grid]"
    tree5 = ast.parse(code5)
    findings5 = DataFlowTracer(tree5, code5).trace()
    assert any(f['pattern'] == 'nested_listcomp' for f in findings5), \
        f"Missing nested_listcomp finding: {findings5}"

    print("DataFlowTracer       OK  findings=%d" % len(findings1 + findings2 + findings3 + findings5))
except Exception as e:
    errors.append(f"DataFlowTracer FAIL: {e}")
    print(f"DataFlowTracer FAIL: {e}")

# ── Engine 5: AntiPatternDetector ────────────────────────────────────────────
try:
    from analyzer.anti_pattern_detector import AntiPatternDetector

    # bare_except + mutable_default_arg
    code = "def foo(x=[]):\n    pass\ntry:\n    pass\nexcept:\n    pass"
    tree = ast.parse(code)
    ap = AntiPatternDetector(tree, code).detect()
    assert any(f['pattern'] == 'bare_except' for f in ap), \
        f"Missing bare_except: {ap}"
    assert any(f['pattern'] == 'mutable_default_arg' for f in ap), \
        f"Missing mutable_default_arg: {ap}"

    # global_modification
    code2 = "counter = 0\ndef inc():\n    global counter\n    counter += 1"
    tree2 = ast.parse(code2)
    ap2 = AntiPatternDetector(tree2, code2).detect()
    assert any(f['pattern'] == 'global_modification' for f in ap2), \
        f"Missing global_modification: {ap2}"

    # return_in_loop
    code3 = "for x in arr:\n    return x"
    tree3 = ast.parse(code3)
    ap3 = AntiPatternDetector(tree3, code3).detect()
    assert any(f['pattern'] == 'return_in_loop' for f in ap3), \
        f"Missing return_in_loop: {ap3}"

    print("AntiPatternDetector  OK  findings=%d" % len(ap))
except Exception as e:
    errors.append(f"AntiPatternDetector FAIL: {e}")
    print(f"AntiPatternDetector FAIL: {e}")

# ── Summary ──────────────────────────────────────────────────────────────────
print()
if errors:
    print("FAILURES:")
    for err in errors:
        print(" ", err)
    sys.exit(1)
else:
    print("ALL 5 ENGINES PASSED")
    sys.exit(0)
