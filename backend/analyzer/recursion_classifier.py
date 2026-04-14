"""
recursion_classifier.py
───────────────────────
Classifies recursion type and complexity using ONLY Python's built-in ast module.
No third-party analysis libraries are used.

Author: AI Code Analyzer
"""

import ast


class RecursionClassifier:
    """
    Walks a Python AST and classifies any recursive function it finds.

    Detect patterns:
        - none          → not recursive
        - linear        → 1 self-call, argument is (n - 1)  → O(n)
        - binary        → 2+ self-calls, no floor-div        → O(2^n)
        - divide_conquer→ 2 self-calls where argument uses // → O(n log n)

    Also checks:
        - Tail recursion  (return <direct self-call>)
        - Memoization     (@lru_cache / @cache decorator)
    """

    def __init__(self, tree: ast.AST, source_code: str) -> None:
        self.tree = tree
        self.source_code = source_code  # kept for potential future use

    # ── Public API ────────────────────────────────────────────────────────────

    def classify(self) -> dict:
        """
        Returns:
            {
                "is_recursive":    bool,
                "pattern":         "none" | "linear" | "binary" | "divide_conquer",
                "complexity_hint": str,
                "is_tail":         bool,
                "is_memoized":     bool,
            }
        """
        _not_recursive = {
            "is_recursive": False,
            "pattern": "none",
            "complexity_hint": "N/A",
            "is_tail": False,
            "is_memoized": False,
        }

        # Inspect every function definition in the module
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result = self._classify_function(node)
                if result["is_recursive"]:
                    return result  # return first recursive function found

        return _not_recursive

    # ── Private helpers ───────────────────────────────────────────────────────

    def _classify_function(self, func_node) -> dict:
        """Inspect a single function definition and return its recursion profile."""
        fname = func_node.name

        # Collect every direct self-call inside the function body
        recursive_calls = [
            node
            for node in ast.walk(func_node)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == fname
            )
        ]

        if not recursive_calls:
            return {
                "is_recursive": False,
                "pattern": "none",
                "complexity_hint": "N/A",
                "is_tail": False,
                "is_memoized": False,
            }

        is_memoized = self._check_memoization(func_node)
        is_tail = self._check_tail_recursion(func_node, fname)
        call_count = len(recursive_calls)

        # ── Determine pattern ─────────────────────────────────────────────
        # Also check if the function body computes a floor-div variable
        # (common in merge_sort: mid = len(arr) // 2, then arr[:mid])
        body_uses_floor_div = self._body_assigns_floor_div(func_node)

        if call_count >= 2:
            # Check whether any recursive call uses floor-division (n // 2)
            # either directly in the arg or via a slice with a floor-div midpoint
            uses_floor_div = (
                any(self._arg_uses_floor_div(call) for call in recursive_calls)
                or any(self._arg_uses_slice(call) for call in recursive_calls)
                and body_uses_floor_div
            )
            if uses_floor_div:
                pattern = "divide_conquer"
                complexity_hint = "O(n log n)"
            else:
                pattern = "binary"
                complexity_hint = "O(2^n)"
        else:
            # Single recursive call
            call = recursive_calls[0]
            if self._arg_uses_floor_div(call) or (
                self._arg_uses_slice(call) and body_uses_floor_div
            ):
                # e.g. binary_search(arr, n // 2)  or  merge_sort(arr[:mid])
                pattern = "divide_conquer"
                complexity_hint = "O(log n)"
            else:
                # e.g. factorial(n - 1) or fib(n - 1)
                pattern = "linear"
                complexity_hint = "O(n)"

        # Memoization overrides the complexity estimate
        if is_memoized:
            complexity_hint = "O(n) due to memoization"

        return {
            "is_recursive": True,
            "pattern": pattern,
            "complexity_hint": complexity_hint,
            "is_tail": is_tail,
            "is_memoized": is_memoized,
        }

    # ── Static helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _arg_uses_floor_div(call_node: ast.Call) -> bool:
        """Return True if ANY positional arg to the call uses // (FloorDiv) directly."""
        for arg in call_node.args:
            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.FloorDiv):
                return True
        return False

    @staticmethod
    def _arg_uses_slice(call_node: ast.Call) -> bool:
        """Return True if any positional arg is a Slice / Subscript (arr[:mid])."""
        for arg in call_node.args:
            if isinstance(arg, ast.Subscript):
                return True
        return False

    @staticmethod
    def _body_assigns_floor_div(func_node) -> bool:
        """
        Return True if the function body contains any assignment where the
        right-hand side is (or contains) a FloorDiv BinOp.
        Catches:  mid = len(arr) // 2
        """
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assign):
                for sub in ast.walk(node.value):
                    if isinstance(sub, ast.BinOp) and isinstance(sub.op, ast.FloorDiv):
                        return True
        return False

    @staticmethod
    def _check_memoization(func_node) -> bool:
        """
        Return True if the function is decorated with lru_cache or cache.
        Handles: @lru_cache, @cache, @functools.lru_cache, @lru_cache(maxsize=…)
        """
        for dec in func_node.decorator_list:
            # Bare name  →  @lru_cache  or  @cache
            if isinstance(dec, ast.Name) and dec.id in ("lru_cache", "cache"):
                return True
            # Attribute  →  @functools.lru_cache
            if isinstance(dec, ast.Attribute) and dec.attr in ("lru_cache", "cache"):
                return True
            # Called form  →  @lru_cache(maxsize=None)
            if isinstance(dec, ast.Call):
                inner = dec.func
                if isinstance(inner, ast.Name) and inner.id in ("lru_cache", "cache"):
                    return True
                if isinstance(inner, ast.Attribute) and inner.attr in ("lru_cache", "cache"):
                    return True
        return False

    @staticmethod
    def _check_tail_recursion(func_node, fname: str) -> bool:
        """
        Return True only when the recursive call is the *direct* value of
        a Return statement (true tail position).

            return factorial(n - 1)      ← tail  ✓
            return n * factorial(n - 1)  ← NOT tail (call is inside BinOp)
        """
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return) and node.value is not None:
                if (
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == fname
                ):
                    return True
        return False
