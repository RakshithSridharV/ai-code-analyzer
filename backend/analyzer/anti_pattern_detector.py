"""
anti_pattern_detector.py
─────────────────────────
Detects code quality anti-patterns using ONLY Python's built-in ast module.
No third-party analysis libraries are used.

Five patterns detected (distinct from DataFlowTracer's data-flow patterns):
    1. redundant_assignment   → constant assigned every loop iteration
    2. return_in_loop         → unguarded return inside loop (exits on first iter)
    3. bare_except            → except: with no type (catches BaseException)
    4. mutable_default_arg    → list/dict/set as function parameter default
    5. global_modification    → global statement inside a function

Complements pattern_detector.py (which handles complexity-level patterns).

Author: AI Code Analyzer
"""

import ast
from typing import Any


class AntiPatternDetector:
    """
    Detect the 5 code quality anti-patterns listed above.
    Each finding is a dict:
        {
            "line":     int,
            "pattern":  str,
            "variable": str,
            "message":  str,
            "severity": "high" | "medium" | "low",
        }
    """

    def __init__(self, tree: ast.AST, source_code: str) -> None:
        self.tree = tree
        self.source_code = source_code  # reserved for future source-level checks

    # ── Public API ────────────────────────────────────────────────────────────

    def detect(self) -> list[dict[str, Any]]:
        """Run all 5 checks and return a merged list of findings."""
        findings: list[dict] = []
        findings.extend(self._check_redundant_assignment_in_loop())
        findings.extend(self._check_return_inside_loop())
        findings.extend(self._check_bare_except())
        findings.extend(self._check_mutable_default_arg())
        findings.extend(self._check_global_modification())
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

    # ── Pattern 1: Redundant constant assignment in loop ──────────────────────

    def _check_redundant_assignment_in_loop(self) -> list[dict]:
        """
        Heuristic: A variable is assigned the same constant every iteration
        with no dependence on the loop variable.
        We flag: assignments whose RHS is an ast.Constant and whose LHS is
        not the loop iteration variable.
        """
        findings: list[dict] = []

        for node in ast.walk(self.tree):
            if not isinstance(node, (ast.For, ast.While)):
                continue

            # Identify the loop variable (for-loop only)
            loop_vars: set[str] = set()
            if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
                loop_vars.add(node.target.id)

            for child in ast.walk(node):
                if child is node:
                    continue
                if isinstance(child, ast.Assign) and isinstance(child.value, ast.Constant):
                    for t in child.targets:
                        if isinstance(t, ast.Name) and t.id not in loop_vars:
                            findings.append(self._finding(
                                line=child.lineno,
                                pattern="redundant_assignment",
                                variable=t.id,
                                message=(
                                    f"'{t.id}' is assigned a constant value every"
                                    f" iteration (line {child.lineno}) with no"
                                    " dependence on the loop variable."
                                    " Move it before the loop."
                                ),
                                severity="low",
                            ))
        return findings

    # ── Pattern 2: Unguarded return inside loop ───────────────────────────────

    def _check_return_inside_loop(self) -> list[dict]:
        """
        An unguarded `return` directly in a loop body exits on the very first
        iteration without processing the rest of the collection.
        We only flag returns that are *direct* children of the loop body (not
        wrapped in an `if` — those are intentional early-return guards).
        """
        findings: list[dict] = []

        for node in ast.walk(self.tree):
            if not isinstance(node, (ast.For, ast.While)):
                continue
            # Inspect only direct children of the loop body
            for stmt in node.body:
                if isinstance(stmt, ast.Return):
                    findings.append(self._finding(
                        line=stmt.lineno,
                        pattern="return_in_loop",
                        variable="",
                        message=(
                            f"return inside loop (line {stmt.lineno}) —"
                            " this exits on the first iteration. Intentional?"
                        ),
                        severity="medium",
                    ))
        return findings

    # ── Pattern 3: Bare except clause ────────────────────────────────────────

    def _check_bare_except(self) -> list[dict]:
        """
        `except:` with no exception type catches *everything*, including
        KeyboardInterrupt and SystemExit — almost always a bug.
        """
        findings: list[dict] = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                findings.append(self._finding(
                    line=node.lineno,
                    pattern="bare_except",
                    variable="",
                    message=(
                        f"Bare except: (line {node.lineno}) catches everything"
                        " including KeyboardInterrupt."
                        " Specify the exception type."
                    ),
                    severity="high",
                ))
        return findings

    # ── Pattern 4: Mutable default argument ──────────────────────────────────

    def _check_mutable_default_arg(self) -> list[dict]:
        """
        Default values are evaluated ONCE at function definition time.
        Using a mutable default (list, dict, set) means all callers share
        the same object — a classic Python gotcha.
        """
        findings: list[dict] = []

        for node in ast.walk(self.tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            args = node.args
            pos_args = args.args

            # defaults aligns to the *last* len(defaults) args
            for i, default in enumerate(args.defaults):
                if not isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    continue
                # Match the default to its parameter
                param_index = len(pos_args) - len(args.defaults) + i
                if param_index < 0 or param_index >= len(pos_args):
                    continue
                param = pos_args[param_index]
                default_repr = (
                    "[]" if isinstance(default, ast.List)
                    else "{}" if isinstance(default, (ast.Dict, ast.Set))
                    else "mutable"
                )
                findings.append(self._finding(
                    line=node.lineno,
                    pattern="mutable_default_arg",
                    variable=param.arg,
                    message=(
                        f"Mutable default argument {param.arg}={default_repr}"
                        f" (line {node.lineno}) — shared across all calls."
                        " Use None and assign inside the function."
                    ),
                    severity="high",
                ))

        return findings

    # ── Pattern 5: Global variable modification ───────────────────────────────

    def _check_global_modification(self) -> list[dict]:
        """
        A `global` statement inside a function means the function reads/writes
        module-level state, making it impure, hard to test, and prone to bugs.
        """
        findings: list[dict] = []

        for func in ast.walk(self.tree):
            if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(func):
                if isinstance(node, ast.Global):
                    for name in node.names:
                        findings.append(self._finding(
                            line=node.lineno,
                            pattern="global_modification",
                            variable=name,
                            message=(
                                f"Global variable '{name}' modified"
                                f" (line {node.lineno}) —"
                                " makes the function impure and hard to test."
                            ),
                            severity="medium",
                        ))
        return findings
