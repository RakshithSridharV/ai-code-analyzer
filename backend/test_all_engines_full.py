import sys, ast, textwrap
sys.path.insert(0, '.')

from analyzer.inference_engine import InferenceEngine
from analyzer.recursion_classifier import RecursionClassifier
from analyzer.data_flow_tracer import DataFlowTracer
from analyzer.anti_pattern_detector import AntiPatternDetector
from analyzer.explanation_builder import ExplanationBuilder

PASS = 0
FAIL = 0

def check(label, condition, got, expected_desc):
    global PASS, FAIL
    status = "PASS" if condition else "FAIL"
    if condition:
        PASS += 1
        print(f"  [{status}] {label}")
    else:
        FAIL += 1
        print(f"  [{status}] {label}")
        print(f"         expected: {expected_desc}")
        print(f"         got:      {got}")

def section(title):
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)

def ie(code):
    tree = ast.parse(textwrap.dedent(code))
    return InferenceEngine(tree, textwrap.dedent(code)).analyze()

def rc(code):
    tree = ast.parse(textwrap.dedent(code))
    return RecursionClassifier(tree, textwrap.dedent(code)).classify()

def dft(code):
    code = textwrap.dedent(code)
    tree = ast.parse(code)
    return DataFlowTracer(tree, code).trace()

def apd(code):
    code = textwrap.dedent(code)
    tree = ast.parse(code)
    return AntiPatternDetector(tree, code).detect()

def eb(code, fn_name):
    code = textwrap.dedent(code)
    tree = ast.parse(code)
    ie_result = InferenceEngine(tree, code).analyze()
    return ExplanationBuilder(ie_result, code, fn_name).build()


# ════════════════════════════════════════════════════════════
section("ENGINE 1 — InferenceEngine")
# ════════════════════════════════════════════════════════════

# Test 1: Constant loop → O(1)
r = ie("""
def print_ten():
    for i in range(10):
        print(i)
""")
check("Constant range(10) loop → O(1)", r["time"] == "O(1)", r["time"], "O(1)")

# Test 2: Linear loop → O(n)
r = ie("""
def find_max(arr):
    max_val = arr[0]
    for item in arr:
        if item > max_val:
            max_val = item
    return max_val
""")
check("Linear loop → O(n)", r["time"] == "O(n)", r["time"], "O(n)")
check("Linear loop → O(1) space", r["space"] == "O(1)", r["space"], "O(1)")

# Test 3: Nested loops → O(n²)
r = ie("""
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
""")
check("Nested loops → O(n²)", r["time"] == "O(n^2)", r["time"], "O(n^2)")

# Test 4: While with //= 10 → O(log n)
r = ie("""
def count_digits(n):
    count = 0
    while n > 0:
        n //= 10
        count += 1
    return count
""")
check("While n//=10 → O(log n)", r["time"] == "O(log n)", r["time"], "O(log n)")

# Test 5: Outer O(n), inner constant range(5) → O(n)
r = ie("""
def process(arr):
    result = []
    for item in arr:
        for j in range(5):
            result.append(item * j)
    return result
""")
check("Outer O(n) + inner range(5) → O(n), NOT O(n²)", r["time"] == "O(n)", r["time"], "O(n)")


# ════════════════════════════════════════════════════════════
section("ENGINE 4 — RecursionClassifier")
# ════════════════════════════════════════════════════════════

# Test 1: Linear recursion (factorial)
r = rc("""
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
""")
check("Factorial → pattern=linear",        r["pattern"] == "linear",  r["pattern"], "linear")
check("Factorial → is_tail=False",         r["is_tail"] == False,     r["is_tail"], False)
check("Factorial → is_memoized=False",     r["is_memoized"] == False, r["is_memoized"], False)
check("Factorial → complexity O(n)",       "O(n)" in r["complexity_hint"], r["complexity_hint"], "contains O(n)")

# Test 2: Tail recursion
r = rc("""
def factorial(n, acc=1):
    if n == 0:
        return acc
    return factorial(n - 1, n * acc)
""")
check("Tail factorial → pattern=linear",   r["pattern"] == "linear",  r["pattern"], "linear")
check("Tail factorial → is_tail=True",     r["is_tail"] == True,      r["is_tail"], True)

# Test 3: Binary recursion (fibonacci)
r = rc("""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
""")
check("Fib → pattern=binary",              r["pattern"] == "binary",   r["pattern"], "binary")
check("Fib → complexity O(2^n)",           "O(2^n)" in r["complexity_hint"], r["complexity_hint"], "contains O(2^n)")
check("Fib → is_memoized=False",           r["is_memoized"] == False,  r["is_memoized"], False)

# Test 4: Memoized recursion
r = rc("""
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
""")
check("Memoized fib → is_memoized=True",   r["is_memoized"] == True,  r["is_memoized"], True)
check("Memoized fib → complexity NOT O(2^n)", "O(2^n)" not in r["complexity_hint"], r["complexity_hint"], "NOT O(2^n)")

# Test 5: Divide and conquer (merge sort)
r = rc("""
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)
""")
check("Merge sort → pattern=divide_conquer", r["pattern"] == "divide_conquer", r["pattern"], "divide_conquer")
check("Merge sort → complexity O(n log n)",  "O(n log n)" in r["complexity_hint"], r["complexity_hint"], "contains O(n log n)")


# ════════════════════════════════════════════════════════════
section("ENGINE 3 — DataFlowTracer")
# ════════════════════════════════════════════════════════════

# Test 1: List membership
r = dft("""
def remove_duplicates(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
""")
has_lm = any(f["pattern"] == "list_membership" for f in r)
check("List membership → flagged", has_lm, [f["pattern"] for f in r], "list_membership")

# Test 2: String concat in loop
r = dft("""
def build_string(words):
    result = ""
    for word in words:
        result += word
    return result
""")
has_sc = any(f["pattern"] == "string_concat_loop" for f in r)
check("String concat in loop → flagged", has_sc, [f["pattern"] for f in r], "string_concat_loop")

# Test 3: len() in loop
r = dft("""
def print_all(arr):
    for i in range(len(arr)):
        print(arr[i])
""")
has_len = any(f["pattern"] == "len_in_loop" for f in r)
check("len() in loop → flagged", has_len, [f["pattern"] for f in r], "len_in_loop")

# Test 4: sort then access index [0]
r = dft("""
def get_smallest(numbers):
    numbers.sort()
    return numbers[0]
""")
has_sort = any(f["pattern"] == "sort_then_index" for f in r)
check("Sort then index[0] → flagged", has_sort, [f["pattern"] for f in r], "sort_then_index")

# Test 5: Clean code → NO findings
r = dft("""
def remove_duplicates_fast(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
""")
check("Clean code → zero findings", len(r) == 0, [f["pattern"] for f in r], "[]")


# ════════════════════════════════════════════════════════════
section("ENGINE 5 — AntiPatternDetector")
# ════════════════════════════════════════════════════════════

# Test 1: Mutable default argument
r = apd("""
def add_item(item, collection=[]):
    collection.append(item)
    return collection
""")
has_mda = any(f["pattern"] == "mutable_default_arg" for f in r)
check("Mutable default arg → flagged", has_mda, [f["pattern"] for f in r], "mutable_default_arg")

# Test 2: Bare except
r = apd("""
def divide(a, b):
    try:
        return a / b
    except:
        return None
""")
has_be = any(f["pattern"] == "bare_except" for f in r)
check("Bare except → flagged", has_be, [f["pattern"] for f in r], "bare_except")

# Test 3: Global modification
r = apd("""
count = 0

def increment():
    global count
    count += 1
""")
has_gm = any(f["pattern"] == "global_modification" for f in r)
check("Global modification → flagged", has_gm, [f["pattern"] for f in r], "global_modification")

# Test 4: Return inside loop
r = apd("""
def process_all(items):
    for item in items:
        result = item * 2
        return result
""")
has_ril = any(f["pattern"] == "return_in_loop" for f in r)
check("Return in loop → flagged", has_ril, [f["pattern"] for f in r], "return_in_loop")


# ════════════════════════════════════════════════════════════
section("ENGINE 2 — ExplanationBuilder (language quality)")
# ════════════════════════════════════════════════════════════

fib_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
"""
explanation = eb(fib_code, "fibonacci")
print(f"\n  Generated explanation:\n  \"{explanation}\"\n")

check("Explanation contains fn name 'fibonacci'",
      "fibonacci" in explanation.lower(), explanation[:100], "contains 'fibonacci'")
check("Explanation mentions recursion / calls itself",
      any(w in explanation.lower() for w in ["recursive", "calls itself", "recursion"]),
      explanation[:100], "contains 'recursive'/'calls itself'")
check("Explanation mentions no memoization / no cache",
      any(w in explanation.lower() for w in ["no memo", "no cache", "without memo", "without cache",
                                              "not memoized", "unmemoized", "no lru", "exponential"]),
      explanation[:120], "contains memoization warning")


# ════════════════════════════════════════════════════════════
section("THE COMBINED TEST — find_duplicates (all 5 engines)")
# ════════════════════════════════════════════════════════════

combined_code = textwrap.dedent("""
def find_duplicates(arr):
    result = []
    for i in range(len(arr)):
        for j in range(len(arr)):
            if arr[i] == arr[j] and i != j:
                if arr[i] not in result:
                    result += str(arr[i])
    return result
""")

tree = ast.parse(combined_code)

# InferenceEngine
ie_r = InferenceEngine(tree, combined_code).analyze()
check("Combined → InferenceEngine O(n²)",  ie_r["time"] == "O(n^2)",  ie_r["time"], "O(n^2)")
check("Combined → InferenceEngine O(n) space", ie_r["space"] == "O(n)", ie_r["space"], "O(n)")

# RecursionClassifier
rc_r = RecursionClassifier(tree, combined_code).classify()
check("Combined → not recursive",           rc_r["is_recursive"] == False, rc_r["is_recursive"], False)

# DataFlowTracer
dft_patterns = [f["pattern"] for f in DataFlowTracer(tree, combined_code).trace()]
check("Combined → len_in_loop flagged",         "len_in_loop" in dft_patterns,         dft_patterns, "len_in_loop")
check("Combined → list_membership flagged",     "list_membership" in dft_patterns,     dft_patterns, "list_membership")
check("Combined → string_concat_loop flagged",  "string_concat_loop" in dft_patterns,  dft_patterns, "string_concat_loop")
print(f"  [INFO] DataFlowTracer findings: {dft_patterns}")

# ExplanationBuilder
expl = eb(combined_code, "find_duplicates")
check("Combined → explanation names 'find_duplicates'",
      "find_duplicates" in expl.lower(), expl[:120], "contains 'find_duplicates'")
check("Combined → explanation says O(n²)",
      any(x in expl for x in ["O(n²)", "O(n^2)", "n²", "quadratic"]),
      expl[:120], "contains O(n²)")
print(f"  [INFO] Explanation: \"{expl[:120]}...\"")


# ════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ════════════════════════════════════════════════════════════
total = PASS + FAIL
print()
print("=" * 60)
print(f"  RESULTS: {PASS}/{total} PASSED  |  {FAIL} FAILED")
print("=" * 60)
if FAIL > 0:
    print("  ACTION REQUIRED: Some engines need fixes (see FAIL lines above)")
    sys.exit(1)
else:
    print("  ALL ENGINES FULLY VERIFIED")
    sys.exit(0)
