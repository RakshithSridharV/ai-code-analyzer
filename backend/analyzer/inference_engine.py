"""
inference_engine.py
───────────────────
Infers time AND space complexity using ONLY Python's built-in ast module.
No third-party analysis libraries are used.

Replaces:  time_complexity.py + space_complexity.py

Author: AI Code Analyzer
"""

import ast
from analyzer.recursion_classifier import RecursionClassifier


# ── Complexity ordering (higher index = worse) ────────────────────────────────
_ORDER: dict[str, int] = {
    "O(1)":       0,
    "O(log n)":   1,
    "O(n)":       2,
    "O(n log n)": 3,
    "O(n^2)":     4,
    "O(n^3)":     5,
    "O(2^n)":     6,
}

# Number of recursive calls implied by each RecursionClassifier pattern
_CALL_COUNT: dict[str, int] = {
    "none": 0, "linear": 1, "binary": 2, "divide_conquer": 2
}


def _max_complexity(a: str, b: str) -> str:
    """Return whichever complexity is worse (higher order)."""
    return a if _ORDER.get(a, 0) >= _ORDER.get(b, 0) else b


def _combine_nested(outer: str, inner: str) -> str:
    """
    Multiply two loop complexities when they are nested:
        O(n)      × O(n)      → O(n^2)
        O(n)      × O(log n)  → O(n log n)
        O(n^2)    × O(n)      → O(n^3)
        O(n log n)× O(n)      → O(n^2)   [approximation]
        O(*)      × O(1)      → outer    [constant inner changes nothing]
        O(1)      × O(*)      → inner
    """
    if inner == "O(1)":
        return outer
    if outer == "O(1)":
        return inner
    if outer == "O(n)" and inner == "O(n)":
        return "O(n^2)"
    if outer == "O(n)" and inner == "O(log n)":
        return "O(n log n)"
    if outer == "O(n^2)" and inner == "O(n)":
        return "O(n^3)"
    if outer == "O(n log n)" and inner == "O(n)":
        return "O(n^2)"
    # Fallback: take whichever is worse
    return _max_complexity(outer, inner)


# ── Internal loop data class ──────────────────────────────────────────────────
class _Loop:
    """Lightweight struct for a single loop's metadata."""
    __slots__ = ("depth", "complexity", "var", "collection", "line")

    def __init__(
        self,
        depth: int,
        complexity: str,
        var: str | None,
        collection: str | None,
        line: int,
    ) -> None:
        self.depth = depth
        self.complexity = complexity
        self.var = var
        self.collection = collection
        self.line = line


# ── Loop visitor ──────────────────────────────────────────────────────────────
class _LoopVisitor(ast.NodeVisitor):
    """
    Walks the AST and records every For / While loop together with
    its nesting depth and estimated per-loop complexity.
    """

    def __init__(self) -> None:
        self.loops: list[_Loop] = []
        self._depth: int = 0

    # -- For -------------------------------------------------------------------
    def visit_For(self, node: ast.For) -> None:
        self._depth += 1
        complexity, var, collection = self._analyze_for_iter(node)
        self.loops.append(_Loop(self._depth, complexity, var, collection, node.lineno))
        self.generic_visit(node)
        self._depth -= 1

    # -- While -----------------------------------------------------------------
    def visit_While(self, node: ast.While) -> None:
        self._depth += 1
        complexity = self._analyze_while_body(node)
        self.loops.append(_Loop(self._depth, complexity, None, None, node.lineno))
        self.generic_visit(node)
        self._depth -= 1

    # -- For iter analysis -----------------------------------------------------
    @staticmethod
    def _analyze_for_iter(node: ast.For) -> tuple[str, str | None, str | None]:
        """
        Examine the loop's iterator to determine per-loop complexity.
        Returns (complexity, loop_variable_name, collection_name).
        """
        iter_node = node.iter
        var = node.target.id if isinstance(node.target, ast.Name) else None

        # ── range(…) ──────────────────────────────────────────────────────
        if (
            isinstance(iter_node, ast.Call)
            and isinstance(iter_node.func, ast.Name)
            and iter_node.func.id == "range"
        ):
            args = iter_node.args

            if len(args) == 1:
                # range(n) — O(n) if n is a variable, O(1) if constant
                arg = args[0]
                if isinstance(arg, ast.Constant):
                    return "O(1)", var, str(arg.value)
                return "O(n)", var, (arg.id if isinstance(arg, ast.Name) else None)

            if len(args) == 2:
                # range(start, stop)
                stop = args[1]
                if isinstance(stop, ast.Constant):
                    return "O(1)", var, str(stop.value)
                return "O(n)", var, (stop.id if isinstance(stop, ast.Name) else None)

            if len(args) == 3:
                # range(start, stop, step) — step > 1 is still O(n) asymptotically
                stop = args[1]
                stop_name = stop.id if isinstance(stop, ast.Name) else None
                if isinstance(stop, ast.Constant):
                    return "O(1)", var, str(stop.value)
                return "O(n)", var, stop_name

        # ── Iterating over a named collection ─────────────────────────────
        if isinstance(iter_node, ast.Name):
            return "O(n)", var, iter_node.id

        # ── Subscript e.g. arr[left:right] ────────────────────────────────
        if isinstance(iter_node, ast.Subscript):
            return "O(n)", var, None

        # ── Any other iterable (list literal, function call, etc.) ─────────
        return "O(n)", var, None

    # -- While body analysis ---------------------------------------------------
    @staticmethod
    def _analyze_while_body(node: ast.While) -> str:
        """
        Heuristic: inspect augmented-assignment operators on the presumed
        loop variable found anywhere inside the while body.

            *=  or  //=   → work space halves each step → O(log n)
            +=            → linear increment            → O(n)
            (anything else / no mod found) → conservative → O(n)
        """
        for child in ast.walk(node):
            if child is node:
                continue
            if isinstance(child, ast.AugAssign):
                if isinstance(child.op, (ast.Mult, ast.FloorDiv)):
                    return "O(log n)"
                if isinstance(child.op, ast.Add):
                    return "O(n)"
        return "O(n)"  # conservative: could be infinite, but O(n) is safest label


# ── Main engine ───────────────────────────────────────────────────────────────
class InferenceEngine:
    """
    Infers time and space complexity from a Python AST using structural rules.
    Combines loop-nesting analysis with recursion classification.
    """

    def __init__(self, tree: ast.AST, source_code: str) -> None:
        self.tree = tree
        self.source_code = source_code

    # ── Public API ────────────────────────────────────────────────────────────

    def analyze(self) -> dict:
        """
        Returns:
            {
                "time":      str,          e.g. "O(n^2)"
                "space":     str,          e.g. "O(n)"
                "reasoning": dict,         used by ExplanationBuilder
            }
        """
        # 1. Walk loops
        visitor = _LoopVisitor()
        visitor.visit(self.tree)
        loops = visitor.loops

        # 2. Classify recursion
        recursion = RecursionClassifier(self.tree, self.source_code).classify()

        # 3. Compute complexities
        time_c, extra_reasoning = self._compute_time(loops, recursion)
        space_c, space_sources = self._compute_space(self.tree, loops)

        # 4. Build reasoning dict (consumed by ExplanationBuilder)
        reasoning = {
            "time_complexity":  time_c,
            "space_complexity": space_c,
            "loops": [
                {
                    "depth":      lp.depth,
                    "var":        lp.var,
                    "collection": lp.collection,
                    "line":       lp.line,
                    "complexity": lp.complexity,
                }
                for lp in loops
            ],
            "recursion": {
                "is_recursive":    recursion["is_recursive"],
                "pattern":         recursion["pattern"],
                "complexity_hint": recursion["complexity_hint"],
                "call_count":      _CALL_COUNT.get(recursion["pattern"], 0),
                "is_tail":         recursion["is_tail"],
                "is_memoized":     recursion["is_memoized"],
                "decorator_name":  self._memoize_decorator_name(),
            },
            "space_sources": space_sources,
            # Outer / inner loop refs populated by _compute_time
            **extra_reasoning,
        }

        return {
            "time":      time_c,
            "space":     space_c,
            "reasoning": reasoning,
        }

    # ── Time complexity ───────────────────────────────────────────────────────

    def _compute_time(
        self, loops: list[_Loop], recursion: dict
    ) -> tuple[str, dict]:
        """
        Fold loop complexities depth-by-depth, then integrate recursion.
        Returns (complexity_string, extra_reasoning_keys_dict).
        """
        extra: dict = {}

        # ── No loops: recursion or constant ──────────────────────────────
        if not loops:
            if recursion["is_recursive"]:
                hint = recursion["complexity_hint"]
                if "memoization" in hint:
                    tc = "O(n)"
                elif "O(2^n)" in hint:
                    tc = "O(2^n)"
                elif "O(n log n)" in hint:
                    tc = "O(n log n)"
                elif "O(log n)" in hint:
                    tc = "O(log n)"
                else:
                    tc = "O(n)"
                return tc, extra
            return "O(1)", extra

        # ── Fold depth-by-depth ───────────────────────────────────────────
        # At each depth, take the worst complexity among all loops at that depth,
        # then combine across depths (nested loops multiply).
        max_depth = max(lp.depth for lp in loops)
        depth_map: dict[int, str] = {}

        for lp in loops:
            prev = depth_map.get(lp.depth, "O(1)")
            depth_map[lp.depth] = _max_complexity(prev, lp.complexity)

        running = "O(1)"
        for depth in range(1, max_depth + 1):
            c = depth_map.get(depth, "O(1)")
            running = _combine_nested(running, c)

        # ── Attach outermost / innermost loop info for ExplanationBuilder ─
        depth1_loops = [lp for lp in loops if lp.depth == 1]
        depth2_loops = [lp for lp in loops if lp.depth == 2]

        if depth1_loops:
            extra["outer_loop"] = {
                "var":        depth1_loops[0].var,
                "collection": depth1_loops[0].collection,
                "line":       depth1_loops[0].line,
            }
        if depth2_loops:
            extra["inner_loop"] = {
                "var":        depth2_loops[0].var,
                "collection": depth2_loops[0].collection,
                "line":       depth2_loops[0].line,
            }

        return running, extra

    # ── Space complexity ──────────────────────────────────────────────────────

    def _compute_space(
        self, tree: ast.AST, loops: list[_Loop]
    ) -> tuple[str, list[str]]:
        """
        Returns (space_string, list_of_source_labels).

        Rules (in priority order):
            1. Variable assigned a mutable container AND grown inside a loop → O(n)
            2. List comprehension iterating over a named variable            → O(n)
            3. Nothing dynamic found                                        → O(1)
        """
        sources: list[str] = []

        # Collect variables explicitly assigned list/dict/set literals
        mutable_vars: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
                    for t in node.targets:
                        if isinstance(t, ast.Name):
                            mutable_vars.add(t.id)
            elif isinstance(node, ast.AugAssign):
                if isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
                    if isinstance(node.target, ast.Name):
                        mutable_vars.add(node.target.id)

        # Check whether any mutable var is grown inside a loop body
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child is node:
                        continue

                    # x.append / x.extend / x.add / x.update inside a loop
                    if isinstance(child, ast.Expr) and isinstance(child.value, ast.Call):
                        call = child.value
                        if isinstance(call.func, ast.Attribute):
                            obj = call.func.value
                            method = call.func.attr
                            if (
                                isinstance(obj, ast.Name)
                                and obj.id in mutable_vars
                                and method in ("append", "extend", "add", "update")
                            ):
                                sources.append("appended_in_loop")
                                return "O(n)", sources

                    # x += [...] augmented add on a known list var inside loop
                    if (
                        isinstance(child, ast.AugAssign)
                        and isinstance(child.op, ast.Add)
                        and isinstance(child.target, ast.Name)
                        and child.target.id in mutable_vars
                    ):
                        sources.append("augmented_in_loop")
                        return "O(n)", sources

        # List comprehension over a named iterable → O(n) output space
        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                for gen in node.generators:
                    if isinstance(gen.iter, ast.Name):
                        sources.append("list_comprehension")
                        return "O(n)", sources

        return "O(1)", sources

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _memoize_decorator_name(self) -> str | None:
        """
        Return the decorator name ('lru_cache' or 'cache') if any function
        in the tree is memoized; otherwise return None.
        """
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name) and dec.id in ("lru_cache", "cache"):
                        return dec.id
                    if isinstance(dec, ast.Attribute) and dec.attr in ("lru_cache", "cache"):
                        return dec.attr
                    if isinstance(dec, ast.Call):
                        inner = dec.func
                        if isinstance(inner, ast.Name) and inner.id in ("lru_cache", "cache"):
                            return inner.id
                        if isinstance(inner, ast.Attribute) and inner.attr in ("lru_cache", "cache"):
                            return inner.attr
        return None
