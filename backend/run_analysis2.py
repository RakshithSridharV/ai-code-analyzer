import ast, sys
sys.path.insert(0, '.')
from analyzer.data_flow_tracer import DataFlowTracer
from analyzer.anti_pattern_detector import AntiPatternDetector
from analyzer.dead_code_detector import DeadCodeDetector
from analyzer.type_inferencer import TypeInferencer

cases = [
    ("list_membership", "def remove_dups(items):\n    result = []\n    for item in items:\n        if item not in result:\n            result.append(item)\n    return result\n"),
    ("string_concat",   "def build(words):\n    result = ''\n    for w in words:\n        result += w\n    return result\n"),
    ("sort_then_index", "def get_min(arr):\n    arr.sort()\n    return arr[0]\n"),
    ("mutable_default", "def add(item, collection=[]):\n    collection.append(item)\n    return collection\n"),
    ("bare_except",     "def divide(a, b):\n    try:\n        return a / b\n    except:\n        return None\n"),
    ("dead_code",       "def foo():\n    x = 42\n    return 1\n    print('never')\n"),
]

print(f"{'Function':<18} | {'Engine':<22} | {'Findings'}")
print("-"*80)

for name, code in cases:
    tree = ast.parse(code)
    ti   = TypeInferencer(tree, code).infer()
    dft  = DataFlowTracer(tree, code, ti).trace()
    ap   = AntiPatternDetector(tree, code).detect()
    dc   = DeadCodeDetector(tree, code).detect()

    all_findings = dft + ap + dc

    for f in all_findings:
        print(f"{name:<18} | {f['pattern']:<22} | [{f['severity'].upper()}] {f['message'][:55]}")

    if not all_findings:
        print(f"{name:<18} | {'none':<22} | no findings")deac+++++++++++++++++````