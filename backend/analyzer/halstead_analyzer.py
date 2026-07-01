"""
halstead_analyzer.py
────────────────────
Implements Halstead Complexity Metrics (1977) using ONLY
Python's built-in ast module.

Halstead defined a program in terms of operators and operands:

OPERATORS (things that do something):
  All ast nodes that represent operations:
  - ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
    ast.Pow, ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift
  - ast.And, ast.Or, ast.Not
  - ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.Is, ast.IsNot, ast.In, ast.NotIn
  - ast.Assign (=), ast.AugAssign (+=, etc.)
  - ast.If, ast.While, ast.For, ast.Return, ast.Raise
  - ast.Call (function call itself is an operator)
  - ast.Attribute (dot access is an operator)
  - ast.Subscript ([] access is an operator)

OPERANDS (things that hold values):
  - ast.Name in Load or Store context (variable names)
  - ast.Constant (all literal values: numbers, strings, bools)
  - Function names from ast.Call

METRICS:
  η1 (eta1) = count of DISTINCT operators
  η2 (eta2) = count of DISTINCT operands
  N1        = TOTAL operator occurrences
  N2        = TOTAL operand occurrences

  Vocabulary:  η  = η1 + η2
  Length:      N  = N1 + N2
  Volume:      V  = N × log2(η)        (bits to represent the program)
  Difficulty:  D  = (η1/2) × (N2/η2)  (how hard to write/understand)
  Effort:      E  = D × V              (mental effort to implement)
  Time:        T  = E / 18             (seconds to implement, Halstead's constant)
  Bugs:        B  = V / 3000           (estimated number of bugs, Halstead's formula)

Risk labels for Volume:
  < 100    → "Trivial"
  100-999  → "Small module"
  1000-3999→ "Medium module"
  4000+    → "Large module, consider splitting"

Risk labels for Difficulty:
  < 10     → "Easy to understand"
  10-19    → "Moderate"
  20-29    → "Difficult"
  30+      → "Very difficult"

Risk labels for Bugs:
  < 0.05   → "Low defect probability"
  0.05-0.2 → "Moderate defect probability"
  0.2+     → "High defect probability — review carefully"

Return format:
{
    "eta1": int,         distinct operators
    "eta2": int,         distinct operands
    "N1": int,           total operators
    "N2": int,           total operands
    "vocabulary": int,
    "length": int,
    "volume": float,
    "difficulty": float,
    "effort": float,
    "time_seconds": float,
    "bugs_estimated": float,
    "volume_label": str,
    "difficulty_label": str,
    "bugs_label": str,
}
"""

import ast
import math
from typing import Any

class HalsteadAnalyzer:
    def __init__(self, tree: ast.AST, source_code: str) -> None:
        self.tree = tree
        self.source_code = source_code

    def analyze(self) -> dict[str, Any]:
        """Collect operators and operands then compute all metrics."""
        operators, distinct_operators, operands, distinct_operands = self._collect()
        
        N1 = len(operators)
        N2 = len(operands)
        n1 = len(distinct_operators)
        n2 = len(distinct_operands)
        
        vocabulary = n1 + n2
        length = N1 + N2
        
        if vocabulary > 0:
            volume = length * math.log2(vocabulary)
        else:
            volume = 0.0
            
        if n2 > 0:
            difficulty = (n1 / 2) * (N2 / n2)
        else:
            difficulty = 0.0
            
        effort = difficulty * volume
        time_seconds = effort / 18
        bugs_estimated = volume / 3000
        
        if volume < 100:
            volume_label = "Trivial"
        elif volume < 1000:
            volume_label = "Small module"
        elif volume < 4000:
            volume_label = "Medium module"
        else:
            volume_label = "Large module, consider splitting"
            
        if difficulty < 10:
            difficulty_label = "Easy to understand"
        elif difficulty < 20:
            difficulty_label = "Moderate"
        elif difficulty < 30:
            difficulty_label = "Difficult"
        else:
            difficulty_label = "Very difficult"
            
        if bugs_estimated < 0.05:
            bugs_label = "Low defect probability"
        elif bugs_estimated < 0.2:
            bugs_label = "Moderate defect probability"
        else:
            bugs_label = "High defect probability — review carefully"
            
        return {
            "eta1": n1,
            "eta2": n2,
            "N1": N1,
            "N2": N2,
            "vocabulary": vocabulary,
            "length": length,
            "volume": float(volume),
            "difficulty": float(difficulty),
            "effort": float(effort),
            "time_seconds": float(time_seconds),
            "bugs_estimated": float(bugs_estimated),
            "volume_label": volume_label,
            "difficulty_label": difficulty_label,
            "bugs_label": bugs_label,
        }

    def _collect(self) -> tuple[list, list, list, list]:
        """
        Walk the entire tree.
        Return (operators, distinct_operators, operands, distinct_operands)
        as lists (use sets internally for distinct counts).
        
        For operator identity use the class name:
        ast.Add → "Add", ast.If → "If", etc.
        
        For operand identity:
        ast.Name → use the id string
        ast.Constant → use repr(value) so 1 and "1" are different
        """
        operators = []
        operands = []
        
        operator_types = (
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
            ast.Pow, ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift,
            ast.And, ast.Or, ast.Not,
            ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
            ast.Is, ast.IsNot, ast.In, ast.NotIn,
            ast.Assign, ast.AugAssign,
            ast.If, ast.While, ast.For, ast.Return, ast.Raise,
            ast.Call, ast.Attribute, ast.Subscript
        )
        
        for node in ast.walk(self.tree):
            if isinstance(node, operator_types):
                operators.append(node.__class__.__name__)
                
            if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Load, ast.Store)):
                operands.append(node.id)
            elif isinstance(node, ast.Constant):
                operands.append(repr(node.value))
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    operands.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    operands.append(node.func.attr)

        return operators, list(set(operators)), operands, list(set(operands))
