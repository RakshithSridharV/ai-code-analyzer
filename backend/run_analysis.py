import ast, sys, subprocess
sys.path.insert(0, '.')
from analyzer.inference_engine import InferenceEngine
from analyzer.confidence_estimator import ConfidenceEstimator

cases = [
    ("range_constant", "def f():\n    for i in range(10):\n        print(i)\n"),
    ("range_variable", "def f(arr):\n    for i in range(len(arr)):\n        print(arr[i])\n"),
    ("nested_input",   "def f(arr):\n    for i in range(len(arr)):\n        for j in range(len(arr)):\n            pass\n"),
    ("nested_const",   "def f(arr):\n    for i in range(len(arr)):\n        for j in range(5):\n            pass\n"),
    ("while_log",      "def f(n):\n    i = 1\n    while i < n:\n        i *= 2\n"),
    ("binary_rec",     "def f(n):\n    if n <= 1: return n\n    return f(n-1) + f(n-2)\n"),
]

print(f"{'Function':<18} | {'ASTra':<12} | {'Conf':<6} | {'Radon CC':<10} | {'Note'}")
print("-"*75)

for name, code in cases:
    tree = ast.parse(code)
    ie   = InferenceEngine(tree, code).analyze()
    ce   = ConfidenceEstimator(tree, code, ie).estimate()
    t    = ie['time']
    conf = str(round(ce['time_confidence']*100)) + '%'

    with open('_radon_tmp.py','w') as f:
        f.write(code)

    res = subprocess.run(
        ['python','-m','radon','cc','_radon_tmp.py','-s'],
        capture_output=True, text=True
    )

    radon_out = res.stdout.strip().split('\n')
    cc_line = next((l for l in radon_out if 'f' in l), 'N/A')
    cc = cc_line.strip() if cc_line != 'N/A' else 'N/A'

    notes = {
        "range_constant": "ASTra: O(1) — Radon gives no Big-O",
        "range_variable": "ASTra: O(n) — Radon gives no Big-O",
        "nested_input":   "ASTra: O(n^2) — Radon gives no Big-O",
        "nested_const":   "ASTra: O(n) — Radon gives no Big-O",
        "while_log":      "ASTra: O(log n) — Radon gives no Big-O",
        "binary_rec":     "ASTra: O(2^n) — Radon gives no Big-O",
    }

    print(f"{name:<18} | {t:<12} | {conf:<6} | {cc:<10} | {notes[name]}")