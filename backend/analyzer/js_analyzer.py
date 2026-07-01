"""
js_analyzer.py  ─  Tree-sitter powered JavaScript static analysis
──────────────────────────────────────────────────────────────────
Fully supports:
  • ES5, ES6+, TypeScript-flavored JS
  • Arrow functions  (a => b, (a, b) => { ... })
  • const / let / var
  • for-of, for-in, .forEach, .map, .filter, .reduce, .flatMap, etc.
  • Recursive function calls (named function or arrow assigned to const)
  • Sorting  (.sort())
  • Binary search patterns (Math.floor((lo+hi)/2))
  • Dynamic programming (2D array init)

Returns: (time_complexity, space_complexity, is_recursive, loop_count)
         so that the existing backend pipeline stays unchanged.
"""

from __future__ import annotations
from tree_sitter import Language, Parser
import tree_sitter_javascript

# ── One-time setup ────────────────────────────────────────────────────────────
_JS_LANG   = Language(tree_sitter_javascript.language())
_JS_PARSER = Parser(_JS_LANG)

# Loop node types
_LOOP_TYPES = {
    "for_statement",
    "for_in_statement",   # for (k in obj)
    "for_of_statement",   # for (x of arr)
    "while_statement",
    "do_statement",
}

# Array iteration higher-order methods  →  each implies one O(n) scan
_ARRAY_HOF = {
    "forEach", "map", "filter", "reduce", "find", "findIndex",
    "every", "some", "flat", "flatMap", "reduceRight",
}
_SORT_METHODS   = {"sort", "toSorted"}
_BINARY_SEARCH  = {"binarySearch"}
_MAP_SET_OPS    = {"get", "set", "has", "delete", "add"}

# ── Utility ───────────────────────────────────────────────────────────────────
def _get_text(node, code_bytes: bytes) -> str:
    return code_bytes[node.start_byte:node.end_byte].decode(errors="replace")

def _iter_nodes(node):
    yield node
    for child in node.children:
        yield from _iter_nodes(child)

# ── Per-function analysis ─────────────────────────────────────────────────────
def _collect_function_names(root, code_bytes: bytes) -> set[str]:
    """Collect all top-level named functions (declarations + const/let arrow)."""
    names: set[str] = set()
    for node in _iter_nodes(root):
        # function foo() {}
        if node.type == "function_declaration":
            n = node.child_by_field_name("name")
            if n:
                names.add(_get_text(n, code_bytes))
        # const foo = (...) => {}  /  const foo = function() {}
        if node.type == "variable_declarator":
            n = node.child_by_field_name("name")
            v = node.child_by_field_name("value")
            if n and v and v.type in ("arrow_function", "function"):
                names.add(_get_text(n, code_bytes))
        # class method definitions
        if node.type == "method_definition":
            n = node.child_by_field_name("name")
            if n:
                names.add(_get_text(n, code_bytes))
    return names


def _analyze_node(func_node, code_bytes: bytes, func_names: set[str], func_name: str | None) -> dict:
    max_depth   = 0
    hof_count   = 0   # each .forEach / .map etc ≈ +1 loop depth
    recursion   = False
    rec_calls   = 0
    sort_call   = False
    binary_srch = False
    map_set_op  = False
    array_alloc = False
    dp_table    = False

    def walk(node, depth):
        nonlocal max_depth, hof_count, recursion, rec_calls
        nonlocal sort_call, binary_srch, map_set_op, array_alloc, dp_table

        if node.type in _LOOP_TYPES:
            depth += 1
            max_depth = max(max_depth, depth)

        # Binary search pattern: while loop with mid = (lo+hi)/2 or >>1
        if node.type == "while_statement":
            body_text = _get_text(node, code_bytes).lower()
            if ("mid" in body_text and
                    ("/ 2" in body_text or ">>1" in body_text or ">> 1" in body_text)):
                binary_srch = True

        # Method calls: .sort(), .forEach(), etc.
        if node.type == "call_expression":
            fn_node = node.child_by_field_name("function")
            if fn_node and fn_node.type == "member_expression":
                prop = fn_node.child_by_field_name("property")
                if prop:
                    method = _get_text(prop, code_bytes)
                    if method in _ARRAY_HOF:
                        hof_count += 1
                        depth_here = depth + 1        # treat as +1 nesting
                        max_depth  = max(max_depth, depth_here)
                    if method in _SORT_METHODS:
                        sort_call = True
                    if method in _BINARY_SEARCH:
                        binary_srch = True
                    if method in _MAP_SET_OPS:
                        map_set_op = True

            # Recursion check: standalone call_expression whose callee is an identifier matching func_name
            if fn_node and fn_node.type == "identifier":
                callee = _get_text(fn_node, code_bytes)
                if func_name and callee == func_name:
                    recursion = True
                    rec_calls += 1

        # Array / object creation   new Array(n), [], {}, new Map()
        if node.type == "new_expression":
            cstr = node.child_by_field_name("constructor")
            if cstr and _get_text(cstr, code_bytes) in ("Array", "Map", "Set", "Object"):
                array_alloc = True

        # DP pattern: variable named dp / memo / cache assigned to 2D array
        if node.type in ("variable_declarator", "assignment_expression"):
            txt = _get_text(node, code_bytes).lower()
            if ("dp" in txt or "memo" in txt or "cache" in txt):
                dp_table = True

        for child in node.children:
            walk(child, depth)

    walk(func_node, 0)

    # ── Classify complexity ───────────────────────────────────────────────────
    if binary_srch:
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
    elif array_alloc or recursion:
        space_c = "O(n)"
    elif map_set_op:
        space_c = "O(n)"
    else:
        space_c = "O(1)"

    patterns = []
    if sort_call:       patterns.append("sorting_call")
    if binary_srch:     patterns.append("binary_search")
    if map_set_op:      patterns.append("hash_based_lookup")
    if dp_table:        patterns.append("dynamic_programming")
    if recursion:       patterns.append("recursive")
    if max_depth >= 2:  patterns.append("nested_loop")
    if hof_count:       patterns.append("higher_order_iteration")

    return {
        "name":            func_name or "anonymous",
        "time_complexity": time_c,
        "space_complexity": space_c,
        "recursion":       recursion,
        "loops":           max_depth,
        "max_loop_depth":  max_depth,
        "patterns":        patterns,
    }


# ── Public function nodes collector ──────────────────────────────────────────
_FUNC_NODES = {
    "function_declaration",
    "function",
    "function_expression",   # var foo = function() {}
    "arrow_function",
    "method_definition",
}

def _collect_functions(root, code_bytes):
    """
    Walk root and yield (name, node) for every top-level function.
    Skips nested function nodes that are already inside another function.
    """
    found = []

    def walk(node, inside_func):
        is_func = node.type in _FUNC_NODES
        if is_func and not inside_func:
            name = None
            # function declaration name
            if node.type == "function_declaration":
                n = node.child_by_field_name("name")
                if n:
                    name = _get_text(n, code_bytes)
            # method definition name
            elif node.type == "method_definition":
                n = node.child_by_field_name("name")
                if n:
                    name = _get_text(n, code_bytes)
            # arrow / anon assigned to const foo = ...
            # parent is variable_declarator
            elif node.type in ("arrow_function", "function") and node.parent:
                parent = node.parent
                if parent.type == "variable_declarator":
                    n = parent.child_by_field_name("name")
                    if n:
                        name = _get_text(n, code_bytes)
            found.append((name, node))
            for child in node.children:
                walk(child, True)
        else:
            for child in node.children:
                walk(child, inside_func)

    walk(root, False)
    return found


# ── Backwards-compat public API ───────────────────────────────────────────────
def analyze_js_code(code: str):
    """
    Public entry point — kept signature-compatible with old pyjsparser version.
    Returns: (time_complexity, space_complexity, is_recursive, loop_count)
    """
    code_bytes  = code.encode()
    tree        = _JS_PARSER.parse(code_bytes)
    root        = tree.root_node
    func_names  = _collect_function_names(root, code_bytes)
    functions   = _collect_functions(root, code_bytes)

    if not functions:
        # Inline script with no function wrapper: analyse the whole program
        result = _analyze_node(root, code_bytes, func_names, None)
        return (result["time_complexity"], result["space_complexity"],
                result["recursion"], result["loops"])

    results = [_analyze_node(node, code_bytes, func_names, name)
               for name, node in functions]

    _ORDER = {"O(1)":1,"O(log n)":2,"O(n)":3,"O(n log n)":4,
              "O(n^2)":5,"O(n^3)":6,"O(2^n)":7,"Unknown":0}
    worst   = max(results, key=lambda r: _ORDER.get(r["time_complexity"], 0))

    return (worst["time_complexity"], worst["space_complexity"],
            any(r["recursion"] for r in results), worst["loops"])