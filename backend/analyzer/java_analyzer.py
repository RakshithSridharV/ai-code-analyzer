"""
java_analyzer.py  ─  Tree-sitter powered Java static analysis
──────────────────────────────────────────────────────────────
Parses ANY Java snippet (bare method, inner-class, full class,
LeetCode-style) without crashing.  Uses tree-sitter-java which
is tolerant of missing class declarations.

Returns a structured dict with:
  time_complexity, space_complexity, recursion, loops,
  max_loop_depth, patterns, function_breakdown
"""

from __future__ import annotations
import re
from tree_sitter import Language, Parser
import tree_sitter_java

# ── One-time language/parser setup ───────────────────────────────────────────
_JAVA_LANG   = Language(tree_sitter_java.language())
_JAVA_PARSER = Parser(_JAVA_LANG)

# Nodes that represent loops
_LOOP_TYPES = {
    "for_statement",
    "enhanced_for_statement",   # for (int x : arr)
    "while_statement",
    "do_statement",
    "labeled_statement",        # outer: for(...)
}

# Method calls that imply O(n log n) sorting
_SORT_METHODS  = {"sort", "sorted", "mergeSort", "quickSort", "parallelSort"}
_SET_MAP_OPS   = {"put", "get", "contains", "containsKey", "add", "remove"}
_BINARY_SEARCH = {"binarySearch", "lowerBound", "upperBound"}

# ── Walk helper ───────────────────────────────────────────────────────────────
def _iter_nodes(node):
    """Depth-first generator over every node in the tree."""
    yield node
    for child in node.children:
        yield from _iter_nodes(child)

def _get_text(node, code_bytes: bytes) -> str:
    return code_bytes[node.start_byte : node.end_byte].decode(errors="replace")

# ── Core analyzer ─────────────────────────────────────────────────────────────
def _analyze_function_node(func_node, code_bytes: bytes) -> dict:
    """
    Analyze a single method/function node extracted by tree-sitter.
    Returns dict with complexity info for that function only.
    """
    max_depth   = 0
    recursion   = False
    rec_calls   = 0
    sort_call   = False
    binary_srch = False
    set_map_op  = False
    array_alloc = False
    dp_table    = False

    # Get function name
    func_name = None
    for child in func_node.children:
        if child.type == "identifier":
            func_name = _get_text(child, code_bytes)
            break
    # also try field "name"
    name_node = func_node.child_by_field_name("name")
    if name_node:
        func_name = _get_text(name_node, code_bytes)

    # ── Recursive depth-first to measure loop nesting ────────────────────────
    def walk_depth(node, current_depth):
        nonlocal max_depth, recursion, rec_calls, sort_call
        nonlocal binary_srch, set_map_op, array_alloc, dp_table

        if node.type in _LOOP_TYPES:
            current_depth += 1
            max_depth = max(max_depth, current_depth)

        # Binary search: while loop containing mid = (left+right)/2 or >> 1
        if node.type == "while_statement":
            body_text = code_bytes[node.start_byte:node.end_byte].decode(errors="replace").lower()
            if ("mid" in body_text and
                    ("/2" in body_text or "/ 2" in body_text or
                     ">>1" in body_text or ">> 1" in body_text)):
                binary_srch = True

        # Detect recursion
        if node.type == "method_invocation":
            name_n = node.child_by_field_name("name")
            if name_n and _get_text(name_n, code_bytes) == func_name:
                recursion  = True
                rec_calls += 1

            # Sort / binary-search / set-map patterns
            method_name = _get_text(name_n, code_bytes) if name_n else ""
            obj_node    = node.child_by_field_name("object")
            if method_name in _SORT_METHODS:
                sort_call = True
            if method_name in _BINARY_SEARCH:
                binary_srch = True
            if method_name in _SET_MAP_OPS:
                set_map_op = True

        # Array allocation  (new int[n], new Object[n])
        if node.type == "array_creation_expression":
            array_alloc = True

        # DP table: int[][] dp = new int[m][n]
        if node.type == "variable_declarator":
            text = _get_text(node, code_bytes).lower()
            if "dp" in text or "memo" in text or "cache" in text:
                dp_table = True

        for child in node.children:
            walk_depth(child, current_depth)

    walk_depth(func_node, 0)

    # ── Complexity classification ─────────────────────────────────────────────
    if binary_srch:
        time_c = "O(log n)"
    elif recursion and rec_calls >= 2:
        time_c = "O(2^n)"
    elif recursion and sort_call:
        time_c = "O(n log n)"
    elif recursion:
        time_c = "O(n)"
    elif sort_call and max_depth >= 1:
        time_c = "O(n log n)"
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
    elif array_alloc or recursion:
        space_c = "O(n)"
    elif set_map_op:
        space_c = "O(n)"
    else:
        space_c = "O(1)"

    patterns = []
    if sort_call:       patterns.append("sorting_call")
    if binary_srch:     patterns.append("binary_search")
    if set_map_op:      patterns.append("hash_based_lookup")
    if dp_table:        patterns.append("dynamic_programming")
    if recursion:       patterns.append("recursive")
    if max_depth >= 2:  patterns.append("nested_loop")

    return {
        "name":            func_name or "anonymous",
        "time_complexity": time_c,
        "space_complexity": space_c,
        "recursion":       recursion,
        "loops":           max_depth,
        "max_loop_depth":  max_depth,
        "patterns":        patterns,
    }

# ── Public interface ───────────────────────────────────────────────────────────
def analyze_java_code(code: str) -> dict:
    """
    Analyze Java code (any snippet, class, or method).
    Always returns a valid dict — never raises.
    """
    code_bytes = code.encode()
    tree = _JAVA_PARSER.parse(code_bytes)
    root = tree.root_node

    # Collect all method declarations in the tree
    methods = [n for n in _iter_nodes(root) if n.type == "method_declaration"]

    if not methods:
        # No method found — still do a best-effort global walk
        global_result = _analyze_function_node(root, code_bytes)
        return {
            "time_complexity":  global_result["time_complexity"],
            "space_complexity": global_result["space_complexity"],
            "recursion":        global_result["recursion"],
            "loops":            global_result["loops"],
            "max_loop_depth":   global_result["max_loop_depth"],
            "patterns":         global_result["patterns"],
            "function_breakdown": [],
        }

    # Analyse each function and pick worst-case for the top-level result
    breakdowns = [_analyze_function_node(m, code_bytes) for m in methods]

    # Complexity ordering for "worst first" selection
    _ORDER = {"O(1)":1,"O(log n)":2,"O(n)":3,"O(n log n)":4,"O(n^2)":5,"O(n^3)":6,"O(2^n)":7,"Unknown":0}
    worst  = max(breakdowns, key=lambda r: _ORDER.get(r["time_complexity"], 0))
    any_rec = any(r["recursion"] for r in breakdowns)
    all_patterns = list({p for r in breakdowns for p in r["patterns"]})

    return {
        "time_complexity":  worst["time_complexity"],
        "space_complexity": worst["space_complexity"],
        "recursion":        any_rec,
        "loops":            worst["loops"],
        "max_loop_depth":   worst["max_loop_depth"],
        "patterns":         all_patterns,
        "function_breakdown": breakdowns,
    }