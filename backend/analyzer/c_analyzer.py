"""
c_analyzer.py  ─  Tree-sitter powered C / C++ static analysis
──────────────────────────────────────────────────────────────
Supports:
  • Bare C snippets  (no #include needed)
  • C99 / C11 / C++ raw method bodies
  • for / while / do-while nested depth
  • Recursive self-calls
  • qsort() / std::sort → O(n log n)
  • Binary search patterns (bsearch, binary_search)
  • Malloc / calloc → O(n) space
  • 2-D array allocation → O(n²) space / DP detection

Returns: (time_complexity, space_complexity, is_recursive, loop_count)
"""

from __future__ import annotations
from tree_sitter import Language, Parser
import tree_sitter_c

# ── One-time setup ────────────────────────────────────────────────────────────
_C_LANG   = Language(tree_sitter_c.language())
_C_PARSER = Parser(_C_LANG)

_LOOP_TYPES = {
    "for_statement",
    "while_statement",
    "do_statement",
}

_SORT_FNS   = {"qsort", "sort", "stable_sort", "mergesort", "heapsort"}
_BSEARCH    = {"bsearch", "binary_search", "lower_bound", "upper_bound"}
_ALLOC_FNS  = {"malloc", "calloc", "realloc", "new", "alloc"}

# ── Utility ───────────────────────────────────────────────────────────────────
def _get_text(node, code_bytes: bytes) -> str:
    return code_bytes[node.start_byte:node.end_byte].decode(errors="replace")

def _iter_nodes(node):
    yield node
    for child in node.children:
        yield from _iter_nodes(child)

# ── Collect top-level function names ─────────────────────────────────────────
def _function_names(root, code_bytes):
    names = set()
    for node in _iter_nodes(root):
        if node.type == "function_definition":
            decl = node.child_by_field_name("declarator")
            if decl:
                for sub in _iter_nodes(decl):
                    if sub.type == "identifier":
                        names.add(_get_text(sub, code_bytes))
                        break
    return names

# ── Per-function analysis ─────────────────────────────────────────────────────
def _analyze_func_node(node, code_bytes: bytes, func_name: str | None) -> dict:
    max_depth   = 0
    recursion   = False
    rec_calls   = 0
    sort_call   = False
    bsearch     = False
    heap_alloc  = False
    dp_table    = False

    def walk(n, depth):
        nonlocal max_depth, recursion, rec_calls
        nonlocal sort_call, bsearch, heap_alloc, dp_table

        if n.type in _LOOP_TYPES:
            depth += 1
            max_depth = max(max_depth, depth)

        # Binary search pattern: while loop with mid = (lo+hi)/2 or >> 1
        if n.type == "while_statement":
            body_text = code_bytes[n.start_byte:n.end_byte].decode(errors="replace").lower()
            if ("mid" in body_text and
                    ("/2" in body_text or "/ 2" in body_text or
                     ">>1" in body_text or ">> 1" in body_text)):
                bsearch = True

        # Function calls
        if n.type == "call_expression":
            fn_n = n.child_by_field_name("function")
            if fn_n:
                # strip namespace qualifiers (std::sort → sort)
                fn_txt = _get_text(fn_n, code_bytes).split("::")[-1].split(".")[-1]
                if fn_txt in _SORT_FNS:
                    sort_call = True
                if fn_txt in _BSEARCH:
                    bsearch = True
                if fn_txt in _ALLOC_FNS:
                    heap_alloc = True
                if func_name and fn_txt == func_name:
                    recursion = True
                    rec_calls += 1

        # DP / memo pattern: variable named dp, memo, cache
        if n.type in ("declaration", "init_declarator"):
            txt = _get_text(n, code_bytes).lower()
            if "dp" in txt or "memo" in txt or "cache" in txt:
                dp_table = True

        for child in n.children:
            walk(child, depth)

    walk(node, 0)

    # ── Classify ──────────────────────────────────────────────────────────────
    if bsearch:
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

    if dp_table:
        space_c = "O(n^2)"
    elif heap_alloc or recursion:
        space_c = "O(n)"
    else:
        space_c = "O(1)"

    patterns = []
    if sort_call:       patterns.append("sorting_call")
    if bsearch:         patterns.append("binary_search")
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

# ── Collect function nodes ────────────────────────────────────────────────────
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
def analyze_c_code(code: str):
    """
    Returns: (time_complexity, space_complexity, is_recursive, loop_count)
    Never raises.
    """
    code_bytes = code.encode()
    tree       = _C_PARSER.parse(code_bytes)
    root       = tree.root_node

    functions  = _collect_functions(root, code_bytes)

    if not functions:
        # bare snippet (no function wrapper)
        r = _analyze_func_node(root, code_bytes, None)
        return r["time_complexity"], r["space_complexity"], r["recursion"], r["loops"]

    _ORDER = {"O(1)":1,"O(log n)":2,"O(n)":3,"O(n log n)":4,
              "O(n^2)":5,"O(n^3)":6,"O(2^n)":7,"Unknown":0}

    results = [_analyze_func_node(node, code_bytes, name) for name, node in functions]
    worst   = max(results, key=lambda r: _ORDER.get(r["time_complexity"], 0))

    return (worst["time_complexity"], worst["space_complexity"],
            any(r["recursion"] for r in results), worst["loops"])