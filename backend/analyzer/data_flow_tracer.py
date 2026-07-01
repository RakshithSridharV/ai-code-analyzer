"""
data_flow_tracer.py
───────────────────
Detects data-flow inefficiency patterns using ONLY Python's built-in ast module.
No third-party analysis libraries are used.

Five patterns detected:
    1. list_membership     → O(n) 'in' check on a list (use set for O(1))
    2. string_concat_loop  → string += in a loop (O(n²); use list + join)
    3. len_in_loop         → len(x) every iteration (hoist before loop)
    4. sort_for_extremum   → sort then only [0]/[-1] (use min/max)
    5. nested_listcomp     → nested list comprehension (O(n²) space)

Author: AI Code Analyzer
"""

import ast
from typing import Any


class DataFlowTracer:
    """
    Walk a Python AST and surface the 5 data-flow inefficiency patterns above.
    Each finding is a dict:
        {
            "line":     int,
            "pattern":  str,
            "variable": str,
            "message":  str,
            "severity": "high" | "medium" | "low",
        }
    """

    def __init__(
        self,
        tree: ast.AST,
        source_code: str,
        type_info: dict | None = None
    ) -> None:
        self.tree = tree
        self.source_code = source_code  # reserved for future source-level checks
        self.type_info = type_info

    # ── Public API ────────────────────────────────────────────────────────────

    def trace(self) -> list[dict[str, Any]]:
        """Run all 5 checks and return a merged list of findings."""
        findings: list[dict] = []
        findings.extend(self._check_list_membership())
        findings.extend(self._check_string_concat_in_loop())
        findings.extend(self._check_len_in_loop())
        findings.extend(self._check_sort_then_index())
        findings.extend(self._check_nested_listcomp())
        return findings

    # ── Shared helper ─────────────────────────────────────────────────────────

    @staticmethod
    def _finding(
        line: int, pattern: str, variable: str, message: str, severity: str
    ) -> dict:
        return {
            "line":     line,
            "pattern":  pattern,
            "variable": variable,
            "message":  message,
            "severity": severity,
        }

    # ── Pattern 1: list used with `in` operator ───────────────────────────────

    def _check_list_membership(self) -> list[dict]:
        """
        Find:   x in some_var  (or x not in some_var)  where some_var is a list.
        Flag:   O(n) membership check — use a set for O(1).

        Detects list vars as:
          - Direct assignment of a list literal:  result = []
          - Var grown via .append() inside any loop body
        """
        # 1. Literal list assignment
        list_vars: set[str] = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        list_vars.add(t.id)

        # 2. Vars grown via .append() inside a loop
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child is node:
                        continue
                    if (
                        isinstance(child, ast.Expr)
                        and isinstance(child.value, ast.Call)
                        and isinstance(child.value.func, ast.Attribute)
                        and child.value.func.attr == "append"
                        and isinstance(child.value.func.value, ast.Name)
                    ):
                        list_vars.add(child.value.func.value.id)

        if self.type_info and "parameter_hints" in self.type_info:
            for param, inferred_type in self.type_info["parameter_hints"].items():
                if inferred_type == "list":
                    list_vars.add(param)

        findings: list[dict] = []
        reported: set[str] = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Compare):
                for op, comp in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.In, ast.NotIn)) and isinstance(comp, ast.Name):
                        if comp.id in list_vars and comp.id not in reported:
                            reported.add(comp.id)
                            findings.append(self._finding(
                                line=node.lineno,
                                pattern="list_membership",
                                variable=comp.id,
                                message=(
                                    f"'{comp.id}' is a list — 'in' check is O(n). "
                                    f"Convert to set for O(1) lookup (line {node.lineno})."
                                ),
                                severity="high",
                            ))
        return findings

    # ── Pattern 2: string concatenation in loop ───────────────────────────────

    def _check_string_concat_in_loop(self) -> list[dict]:
        """
        Find:   str_var += <string expression> inside a For / While body.
        Catches:
          - str_var starts as "" (literal string)
          - str_var += str(...)  — explicit cast to string, regardless of init type
        Flag:   O(n²) concatenation — use a list and ''.join() at the end.
        """
        # Collect vars that start as string literals
        str_vars: set[str] = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                if (
                    isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                ):
                    for t in node.targets:
                        if isinstance(t, ast.Name):
                            str_vars.add(t.id)

        findings: list[dict] = []
        seen: set[str] = set()  # avoid duplicate findings for the same var

        for node in ast.walk(self.tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child is node:
                        continue
                    if (
                        isinstance(child, ast.AugAssign)
                        and isinstance(child.op, ast.Add)
                        and isinstance(child.target, ast.Name)
                        and child.target.id not in seen
                    ):
                        var = child.target.id
                        rhs_is_str_expr = (
                            var in str_vars
                            or self._rhs_is_string_expr(child.value)
                        )
                        if rhs_is_str_expr:
                            seen.add(var)
                            findings.append(self._finding(
                                line=child.lineno,
                                pattern="string_concat_loop",
                                variable=var,
                                message=(
                                    f"String += in loop (line {child.lineno}) is O(n\u00b2). "
                                    "Use a list and ''.join() at the end."
                                ),
                                severity="high",
                            ))
        return findings

    @staticmethod
    def _rhs_is_string_expr(node: ast.expr) -> bool:
        """Return True if node is obviously a string expression (str literal or str() call)."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "str"
        ):
            return True
        return False

    # ── Pattern 3: len() called every iteration ───────────────────────────────

    def _check_len_in_loop(self) -> list[dict]:
        """
        Find:   len(x) inside a For / While body where x doesn't change.
        Flag:   Unnecessary recomputation — hoist before the loop.
        """
        findings: list[dict] = []
        reported: set[str] = set()  # one finding per unique variable

        for node in ast.walk(self.tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child is node:
                        continue
                    if (
                        isinstance(child, ast.Call)
                        and isinstance(child.func, ast.Name)
                        and child.func.id == "len"
                        and child.args
                        and isinstance(child.args[0], ast.Name)
                    ):
                        var = child.args[0].id
                        if var not in reported:
                            reported.add(var)
                            findings.append(self._finding(
                                line=child.lineno,
                                pattern="len_in_loop",
                                variable=var,
                                message=(
                                    f"len({var}) called every iteration"
                                    f" (line {child.lineno}). "
                                    f"Hoist it: n = len({var}) before the loop."
                                ),
                                severity="medium",
                            ))
        return findings

    # ── Pattern 4: sort then only access [0] or [-1] ─────────────────────────

    def _check_sort_then_index(self) -> list[dict]:
        """
        Find:   x.sort() / sorted(x) followed by x[0] or x[-1].
        Flag:   Use min() / max() instead — O(n) vs O(n log n).
        """
        findings: list[dict] = []
        sorted_vars: dict[str, int] = {}  # var_name → line of sort call
        reported: set[str] = set()

        for node in ast.walk(self.tree):
            # x.sort()
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "sort"
                and isinstance(node.value.func.value, ast.Name)
            ):
                sorted_vars[node.value.func.value.id] = node.lineno

            # var = sorted(x)  — record both the result var and the source var
            if isinstance(node, ast.Assign):
                if (
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "sorted"
                ):
                    for t in node.targets:
                        if isinstance(t, ast.Name):
                            sorted_vars[t.id] = node.lineno
                    if node.value.args and isinstance(node.value.args[0], ast.Name):
                        sorted_vars[node.value.args[0].id] = node.lineno

        # Look for subscript access [0] or [-1] on any sorted variable
        for node in ast.walk(self.tree):
            if (
                isinstance(node, ast.Subscript)
                and isinstance(node.value, ast.Name)
                and node.value.id in sorted_vars
            ):
                idx = node.slice
                # Python 3.8 wraps slices in ast.Index; 3.9+ uses the node directly
                if isinstance(idx, ast.Index):          # type: ignore[attr-defined]
                    idx = idx.value                     # type: ignore[attr-defined]
                if isinstance(idx, ast.Constant) and idx.value in (0, -1):
                    var = node.value.id
                    if var not in reported:
                        reported.add(var)
                        sort_line = sorted_vars[var]
                        findings.append(self._finding(
                            line=sort_line,
                            pattern="sort_then_index",
                            variable=var,
                            message=(
                                f"You sort {var} (line {sort_line}) but only"
                                " access index [0]/[-1]. "
                                "Use min()/max() instead — O(n) vs O(n log n)."
                            ),
                            severity="medium",
                        ))
        return findings

    # ── Pattern 5: nested list comprehension ──────────────────────────────────

    def _check_nested_listcomp(self) -> list[dict]:
        """
        Find:   [... for ... in [... for ... in ...]]  — ListComp inside ListComp.
        Flag:   O(n²) space usage.
        """
        findings: list[dict] = []
        outer_lines: set[int] = set()  # deduplicate by outer line

        for outer in ast.walk(self.tree):
            if not isinstance(outer, ast.ListComp):
                continue
            for inner in ast.walk(outer):
                if inner is outer:
                    continue
                if isinstance(inner, ast.ListComp):
                    if outer.lineno not in outer_lines:
                        outer_lines.add(outer.lineno)
                        findings.append(self._finding(
                            line=outer.lineno,
                            pattern="nested_listcomp",
                            variable="",
                            message=(
                                f"Nested list comprehension (line {outer.lineno})"
                                " creates O(n\u00b2) space."
                            ),
                            severity="medium",
                        ))
                    break  # one finding per outer comprehension

        return findings
