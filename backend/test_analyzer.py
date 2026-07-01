import ast, sys
sys.path.insert(0, '.')
from analyzer.inference_engine import InferenceEngine
from analyzer.recursion_classifier import RecursionClassifier
from analyzer.cyclomatic_analyzer import CyclomaticAnalyzer
from analyzer.confidence_estimator import ConfidenceEstimator

test_cases = [
    ('range_constant_O1',    'def f():\n    for i in range(10):\n        print(i)'),
    ('range_variable_On',    'def f(arr):\n    for i in range(len(arr)):\n        print(i)'),
    ('nested_loops_On2',     'def f(arr):\n    for i in range(len(arr)):\n        for j in range(len(arr)):\n            pass'),
    ('while_multiply_Ologn', 'def f(n):\n    i=1\n    while i<n:\n        i*=2'),
    ('linear_recursion',     'def f(n):\n    if n<=1: return 1\n    return n*f(n-1)'),
    ('binary_recursion',     'def f(n):\n    if n<=1: return n\n    return f(n-1)+f(n-2)'),
    ('lru_cache_memoized',   'from functools import lru_cache\n@lru_cache\ndef f(n):\n    if n<=1: return n\n    return f(n-1)+f(n-2)'),
    ('divide_conquer',       'def f(arr):\n    if len(arr)<=1: return arr\n    mid=len(arr)//2\n    return f(arr[:mid])+f(arr[mid:])'),
    ('outer_n_inner_const',  'def f(arr):\n    for i in range(len(arr)):\n        for j in range(5):\n            pass'),
    ('merge_sort_nlogn',     'def f(arr):\n    if len(arr)<=1: return arr\n    m=len(arr)//2\n    l,r=f(arr[:m]),f(arr[m:])\n    res=[]\n    i=j=0\n    while i<len(l) and j<len(r):\n        if l[i]<r[j]: res.append(l[i]); i+=1\n        else: res.append(r[j]); j+=1\n    return res+l[i:]+r[j:]'),
]
expected = ['O(1)','O(n)','O(n^2)','O(log n)','O(n)','O(2^n)','O(n)','O(n log n)','O(n)','O(n log n)']

print("Test Case               | Expected   | ASTra Time | Space  | Cyclo | Conf  | Match")
print("-"*90)
for (name, code), exp in zip(test_cases, expected):
    tree = ast.parse(code)
    ie = InferenceEngine(tree, code).analyze()
    cy = CyclomaticAnalyzer(tree, code).analyze()
    ce = ConfidenceEstimator(tree, code, ie).estimate()
    t  = ie['time']
    sp = ie['space']
    cs = cy['score']
    conf = str(round(ce['time_confidence']*100)) + '%'
    match = 'PASS' if t == exp else 'FAIL got=' + t
    print(f"{name:<24}| {exp:<10} | {t:<10} | {sp:<6} | {cs:<5} | {conf:<5} | {match}")
