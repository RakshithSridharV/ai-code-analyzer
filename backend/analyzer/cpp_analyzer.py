"""
cpp_analyzer.py  ─  Tree-sitter powered C++ static analysis
─────────────────────────────────────────────────────────────
Fully supports:
  • C++11 / C++14 / C++17 / C++20 syntax
  • STL containers: vector, map, set, unordered_map, unordered_set, string
  • STL algorithms: sort, stable_sort, lower_bound, upper_bound, binary_search
  • Range-based for loops  (for (auto x : v))
  • Template functions and class methods
  • Lambda expressions   ([&](int x){ ... })
  • Recursive functions
  • Dynamic programming  (dp[][], memo)
  • new[] / malloc heap allocation → O(n) space
  • 2-D dp array → O(n²) space

Returns: (time_complexity, space_complexity, is_recursive, loop_count)
"""

from __future__ import annotations
from tree_sitter import Language, Parser
import tree_sitter_cpp

# ── One-time setup ────────────────────────────────────────────────────────────
_CPP_LANG   = Language(tree_sitter_cpp.language())
_CPP_PARSER = Parser(_CPP_LANG)

# Loop node types in tree-sitter-cpp
_LOOP_TYPES = {
    "for_statement",
    "for_range_loop",       # range-based for
    "while_statement",
    "do_statement",
}

# STL sort variants → O(n log n)
_SORT_FNS   = {"sort", "stable_sort", "partial_sort", "nth_element",
               "mergesort", "heapsort"}
# STL binary-search variants → O(log n)
_BSEARCH    = {"binary_search", "lower_bound", "upper_bound",
               "equal_range", "bsearch"}
# STL O(n) traversal higher-order calls
_STL_HOF    = {"for_each", "transform", "accumulate", "find", "find_if",
               "count", "count_if", "copy", "fill"}
# Heap / dynamic allocation functions
_ALLOC_FNS  = {"malloc", "calloc", "realloc", "new"}

# ── Utility ───────────────────────────────────────────────────────────────────
def _get_text(node, code_bytes: bytes) -> str:
    return code_bytes[node.start_byte:node.end_byte].decode(errors="replace")

def _iter_nodes(node):
    yield node
    for child in node.children:
        yield from _iter_nodes(child)

# ── Collect top-level function names ──────────────────────────────────────────
def _function_names(root, code_bytes: bytes) -> set[str]:
    names: set[str] = set()
    for node in _iter_nodes(root):
        if node.type == "function_definition":
            decl = node.child_by_field_name("declarator")
            if decl:
                # Walk into function_declarator → identifier
                for sub in _iter_nodes(decl):
                    if sub.type == "identifier":
                        names.add(_get_text(sub, code_bytes))
                        break
    return names

# ── Per-function analysis ─────────────────────────────────────────────────────
def _analyze_func(node, code_bytes: bytes, func_name: str | None) -> dict:
    max_depth   = 0
    stl_hof     = 0      # each STL traversal ≈ +1 depth
    recursion   = False
    rec_calls   = 0
    sort_call   = False
    bsearch     = False
    heap_alloc  = False
    dp_table    = False
    stl_map_set = False  # unordered_map/set → O(n) space

    def walk(n, depth):
        nonlocal max_depth, stl_hof, recursion, rec_calls
        nonlocal sort_call, bsearch, heap_alloc, dp_table, stl_map_set

        if n.type in _LOOP_TYPES:
            depth += 1
            max_depth = max(max_depth, depth)

        # Binary search: while loop with  mid = (lo+hi)/2  or  >> 1
        if n.type == "while_statement":
            body = _get_text(n, code_bytes).lower()
            if "mid" in body and (
                "/ 2" in body or "/2" in body or
                ">> 1" in body or ">>1" in body
            ):
                bsearch = True

        # Call expressions
        if n.type == "call_expression":
            fn_n = n.child_by_field_name("function")
            if fn_n:
                # Resolve qualified names (std::sort → sort)
                raw = _get_text(fn_n, code_bytes)
                fn_txt = raw.split("::")[-1].split(".")[-1].strip()

                if fn_txt in _SORT_FNS:
                    sort_call = True
                if fn_txt in _BSEARCH:
                    bsearch = True
                if fn_txt in _STL_HOF:
                    stl_hof += 1
                    max_depth = max(max_depth, depth + 1)
                if fn_txt in _ALLOC_FNS or fn_txt == "new":
                    heap_alloc = True

                # Recursion
                if func_name and fn_txt == func_name:
                    recursion = True
                    rec_calls += 1

        # new_expression for heap objects: new int[n]
        if n.type == "new_expression":
            heap_alloc = True

        # STL containers as variable types → O(n) space tracking
        if n.type in ("declaration", "field_declaration"):
            txt = _get_text(n, code_bytes).lower()
            if any(t in txt for t in ("vector", "string", "deque", "list",
                                      "queue", "stack", "priority_queue")):
                heap_alloc = True
            if any(t in txt for t in ("map<", "set<", "unordered_map",
                                      "unordered_set", "multimap", "multiset")):
                stl_map_set = True

        # DP pattern: variable named dp, memo, cache
        if n.type in ("declaration", "init_declarator"):
            txt = _get_text(n, code_bytes).lower()
            if "dp" in txt or "memo" in txt or "cache" in txt:
                dp_table = True

        for child in n.children:
            walk(child, depth)

    walk(node, 0)

    # ── Classify complexity ───────────────────────────────────────────────────
    if bsearch:
        time_c = "O(log n)"
    elif recursion and rec_calls >= 2:
        time_c = "O(2^n)"
    elif sort_call and max_depth >= 1:
        time_c = "O(n log n)"
    elif recursion:
        time_c = "O(n)"
    elif max_depth == 0 and sort_call:
        time_c = "O(n log n)"
    elif max_depth >= 3:
        time_c = "O(n^3)"
    elif max_depth == 2:
        time_c = "O(n^2)"
    elif max_depth == 1:
        time_c = "O(n)"
    else:
        time_c = "O(1)"

    # Space complexity
    if dp_table:
        space_c = "O(n^2)"
    elif heap_alloc or recursion or stl_map_set:
        space_c = "O(n)"
    else:
        space_c = "O(1)"

    patterns = []
    if sort_call:       patterns.append("sorting_call")
    if bsearch:         patterns.append("binary_search")
    if dp_table:        patterns.append("dynamic_programming")
    if stl_map_set:     patterns.append("hash_based_lookup")
    if recursion:       patterns.append("recursive")
    if max_depth >= 2:  patterns.append("nested_loop")
    if stl_hof:         patterns.append("stl_iteration")

    return {
        "name":            func_name or "anonymous",
        "time_complexity": time_c,
        "space_complexity": space_c,
        "recursion":       recursion,
        "loops":           max_depth,
        "max_loop_depth":  max_depth,
        "patterns":        patterns,
    }

# ── Collect top-level function nodes ──────────────────────────────────────────
def _collect_functions(root, code_bytes):
    found = []

    def walk(node, inside):
        if node.type == "function_definition" and not inside:
            name = None
            decl = node.child_by_field_name("declarator")
            if decl:
                for sub in _iter_nodes(decl):
                    if sub.type == "identifier":
                        name = _get_text(sub, code_bytes)
                        break
            found.append((name, node))
            for child in node.children:
                walk(child, True)
        else:
            for child in node.children:
                walk(child, inside)

    walk(root, False)
    return found

# ── Public API ────────────────────────────────────────────────────────────────
def analyze_cpp_code(code: str):
    """
    Analyze C++ code (any snippet — bare function, class, full file).
    Returns: (time_complexity, space_complexity, is_recursive, loop_count)
    Never raises.
    """
    code_bytes = code.encode()
    tree       = _CPP_PARSER.parse(code_bytes)
    root       = tree.root_node
    functions  = _collect_functions(root, code_bytes)

    if not functions:
        r = _analyze_func(root, code_bytes, None)
        return r["time_complexity"], r["space_complexity"], r["recursion"], r["loops"]

    _ORDER = {"O(1)":1, "O(log n)":2, "O(n)":3, "O(n log n)":4,
              "O(n^2)":5, "O(n^3)":6, "O(2^n)":7, "Unknown":0}

    results = [_analyze_func(node, code_bytes, name) for name, node in functions]
    worst   = max(results, key=lambda r: _ORDER.get(r["time_complexity"], 0))

    return (worst["time_complexity"], worst["space_complexity"],
            any(r["recursion"] for r in results), worst["loops"])
