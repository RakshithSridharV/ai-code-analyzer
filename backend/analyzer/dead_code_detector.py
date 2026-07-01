"""
dead_code_detector.py
─────────────────────
Detects dead/unreachable code using ONLY Python's built-in ast module.

Five patterns detected:

1. unused_variable
   - Variable is assigned (Store context) but never read (Load context)
     within the same function scope
   - Exclude: variables starting with _ (convention for intentional unused)
   - Exclude: loop variables (for i in ...) if the loop body uses i
   - Flag with: line number, variable name, suggested fix

2. unused_import
   - ast.Import or ast.ImportFrom at module level
   - The imported name never appears in a Load context anywhere in the file
   - Flag: "import X is never used (line N)"

3. unreachable_after_return
   - Any statement that appears in the same block AFTER a Return node
   - e.g.:
       def foo():
           return 1
           print("never")   ← flagged
   - Walk each function's body as a list, find Return, flag everything after

4. unreachable_after_raise
   - Same as above but for Raise nodes
   - Any statement after raise in the same block is unreachable

5. unused_function
   - Function defined at module level (ast.FunctionDef in module body)
   - The function name never appears in a Load or Call context
     anywhere else in the file
   - Exclude: functions named main, __init__, setUp, tearDown,
     and any name starting with test_ or _
   - Flag: "function X is defined but never called (line N)"

Return format per finding:
{
    "line": int,
    "pattern": str,
    "name": str,
    "message": str,
    "severity": "high" | "medium" | "low"
}

severity guide:
  unreachable_after_return / unreachable_after_raise → high
  unused_import → medium
  unused_variable → low
  unused_function → medium
"""

import ast
from typing import Any

class DeadCodeDetector:
    def __init__(self, tree: ast.AST, source_code: str) -> None:
        self.tree = tree
        self.source_code = source_code

    def detect(self) -> list[dict[str, Any]]:
        """Run all 5 checks and return merged findings list."""
        findings = []
        findings.extend(self._check_unused_variables())
        findings.extend(self._check_unused_imports())
        findings.extend(self._check_unreachable_after_return())
        findings.extend(self._check_unreachable_after_raise())
        findings.extend(self._check_unused_functions())
        return findings

    def _check_unused_variables(self) -> list[dict]:
        """
        For each FunctionDef:
        1. Collect all Names in Store context → assigned vars
        2. Collect all Names in Load context → used vars
        3. assigned - used - excluded = unused
        Exclude loop targets that are only used as iteration counters
        """
        findings = []
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                assigned = {}
                used = set()
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Name):
                        if isinstance(child.ctx, ast.Store) or isinstance(child.ctx, ast.Del):
                            if child.id not in assigned:
                                assigned[child.id] = child.lineno
                        elif isinstance(child.ctx, ast.Load):
                            used.add(child.id)
                
                for var_name, lineno in assigned.items():
                    if var_name.startswith('_'):
                        continue
                    if var_name not in used:
                        findings.append({
                            "line": lineno,
                            "pattern": "unused_variable",
                            "name": var_name,
                            "message": f"Variable '{var_name}' is assigned but never used (line {lineno})",
                            "severity": "low"
                        })
        return findings

    def _check_unused_imports(self) -> list[dict]:
        """
        Collect import names at module level.
        Collect all Name ids used in Load context across entire file.
        imported - used = unused imports.
        Handle: import os → name is "os"
        Handle: from os import path → name is "path"
        Handle: import numpy as np → name is "np"
        """
        findings = []
        imports = {}
        for node in self.tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name.split('.')[0]
                    # We store the first occurrence
                    if name not in imports:
                        imports[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name.split('.')[0]
                    if name not in imports:
                        imports[name] = node.lineno

        used = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
                pass 
        
        for name, lineno in imports.items():
            if name not in used:
                findings.append({
                    "line": lineno,
                    "pattern": "unused_import",
                    "name": name,
                    "message": f"import {name} is never used (line {lineno})",
                    "severity": "medium"
                })
        return findings

    def _check_unreachable_after_return(self) -> list[dict]:
        """
        For each function body (list of stmts):
        Find index of first Return.
        Everything after that index in the same list → unreachable.
        Also check nested blocks (if/else/try bodies) recursively.
        """
        findings = []
        def _check_block(body):
            found_return = False
            return_lineno = 0
            for stmt in body:
                if found_return:
                    findings.append({
                        "line": stmt.lineno,
                        "pattern": "unreachable_after_return",
                        "name": "",
                        "message": f"Unreachable code after return (line {return_lineno})",
                        "severity": "high"
                    })
                if isinstance(stmt, ast.Return):
                    found_return = True
                    # Set return_lineno to the line number of the Return node, unless it is already set (the earliest return wins in this scope)
                    if not return_lineno:
                        return_lineno = stmt.lineno
                
                # Check nested blocks
                for field, value in ast.iter_fields(stmt):
                    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], ast.stmt):
                        _check_block(value)
                        
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _check_block(node.body)
        return findings

    def _check_unreachable_after_raise(self) -> list[dict]:
        """Same as above but for Raise nodes."""
        findings = []
        def _check_block(body):
            found_raise = False
            raise_lineno = 0
            for stmt in body:
                if found_raise:
                    findings.append({
                        "line": stmt.lineno,
                        "pattern": "unreachable_after_raise",
                        "name": "",
                        "message": f"Unreachable code after raise (line {raise_lineno})",
                        "severity": "high"
                    })
                if isinstance(stmt, ast.Raise):
                    found_raise = True
                    if not raise_lineno:
                        raise_lineno = stmt.lineno
                
                for field, value in ast.iter_fields(stmt):
                    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], ast.stmt):
                        _check_block(value)
                        
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _check_block(node.body)
        return findings

    def _check_unused_functions(self) -> list[dict]:
        """
        Collect module-level FunctionDef names.
        Collect all Call func names and Name Load ids across file.
        defined - called - excluded = unused.
        """
        findings = []
        defined = {}
        # Only module-level functions
        for node in self.tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined[node.name] = node.lineno
                
        called = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called.add(node.func.attr)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                called.add(node.id)
                
        excluded = {"main", "__init__", "setUp", "tearDown"}
        for name, lineno in defined.items():
            if name in excluded or name.startswith("test_") or name.startswith("_"):
                continue
            if name not in called:
                findings.append({
                    "line": lineno,
                    "pattern": "unused_function",
                    "name": name,
                    "message": f"function {name} is defined but never called (line {lineno})",
                    "severity": "medium"
                })
        return findings
