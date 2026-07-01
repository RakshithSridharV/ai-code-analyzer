"""
type_inferencer.py
──────────────────
Infers variable types from AST without executing the code.
Uses ONLY Python's built-in ast module.

Type inference rules:

LITERAL ASSIGNMENT:
  x = []          → list
  x = {}          → dict (if no values) or dict
  x = set()       → set
  x = ()          → tuple
  x = 0           → int
  x = 0.0         → float
  x = ""          → str
  x = True/False  → bool
  x = None        → NoneType
  x = b""         → bytes

CALL RETURN TYPES (known built-ins):
  len(...)        → int
  range(...)      → range
  str(...)        → str
  int(...)        → int
  float(...)      → float
  list(...)       → list
  dict(...)       → dict
  set(...)        → set
  tuple(...)      → tuple
  sorted(...)     → list
  enumerate(...)  → enumerate
  zip(...)        → zip
  map(...)        → map
  filter(...)     → filter
  sum(...)        → int_or_float
  min(...)        → comparable
  max(...)        → comparable
  abs(...)        → int_or_float
  round(...)      → int_or_float
  bool(...)       → bool
  open(...)       → file

METHOD RETURN TYPES (known patterns):
  x.split(...)    → list   (if x is str)
  x.strip(...)    → str
  x.lower(...)    → str
  x.upper(...)    → str
  x.join(...)     → str
  x.keys(...)     → dict_keys
  x.values(...)   → dict_values
  x.items(...)    → dict_items
  x.get(...)      → unknown (could be None or value type)
  x.append(...)   → None (mutates, returns None)
  x.pop(...)      → unknown

ARITHMETIC INFERENCE:
  int op int      → int
  int op float    → float
  str + str       → str
  list + list     → list

AUGMENTED ASSIGN:
  x += 1  where x is int  → still int
  x += [] where x is list → still list

Return format:
{
    "variables": {
        "var_name": {
            "type": str,          e.g. "list", "int", "str"
            "line": int,          line where type was inferred
            "confidence": float   0.5-1.0
        }
    },
    "parameter_hints": {
        "param_name": str    inferred from how it's used in the function body
    }
}
"""

import ast
from typing import Any

class TypeInferencer:
    def __init__(self, tree: ast.AST, source_code: str) -> None:
        self.tree = tree
        self.source_code = source_code
        self.variables = {}
        self.parameter_hints = {}

    def infer(self) -> dict[str, Any]:
        """
        Walk all FunctionDefs and module-level assignments.
        Return the variables and parameter_hints dicts.
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        inferred_type, confidence = self._infer_type_from_node(node.value)
                        if inferred_type != "unknown":
                            if target.id not in self.variables:
                                self.variables[target.id] = {
                                    "type": inferred_type,
                                    "line": node.lineno,
                                    "confidence": confidence
                                }
            elif isinstance(node, ast.AugAssign):
                if isinstance(node.target, ast.Name):
                    pass
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                hints = self._infer_parameter_hints(node)
                self.parameter_hints.update(hints)

        return {
            "variables": self.variables,
            "parameter_hints": self.parameter_hints
        }

    def _infer_type_from_node(self, node: ast.expr) -> tuple[str, float]:
        """
        Given an AST expression node, return (type_string, confidence).
        This is the core dispatch method.
        """
        if isinstance(node, ast.List) or isinstance(node, ast.ListComp):
            return "list", 1.0
        elif isinstance(node, ast.Dict) or isinstance(node, ast.DictComp):
            return "dict", 1.0
        elif isinstance(node, ast.Set) or isinstance(node, ast.SetComp):
            return "set", 1.0
        elif isinstance(node, ast.Tuple):
            return "tuple", 1.0
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, int) and not isinstance(node.value, bool):
                return "int", 1.0
            elif isinstance(node.value, float):
                return "float", 1.0
            elif isinstance(node.value, str):
                return "str", 1.0
            elif isinstance(node.value, bool):
                return "bool", 1.0
            elif node.value is None:
                return "NoneType", 1.0
            elif isinstance(node.value, bytes):
                return "bytes", 1.0
        elif isinstance(node, ast.Call):
            return self._infer_from_call(node)
        elif isinstance(node, ast.BinOp):
            return self._infer_from_binop(node, {})
        return "unknown", 0.0

    def _infer_from_call(self, node: ast.Call) -> tuple[str, float]:
        """Handle ast.Call nodes using the known built-ins table."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            builtins = {
                "len": "int", "range": "range", "str": "str", "int": "int",
                "float": "float", "list": "list", "dict": "dict", "set": "set",
                "tuple": "tuple", "sorted": "list", "enumerate": "enumerate",
                "zip": "zip", "map": "map", "filter": "filter", "sum": "int_or_float",
                "min": "comparable", "max": "comparable", "abs": "int_or_float",
                "round": "int_or_float", "bool": "bool", "open": "file"
            }
            if func_name in builtins:
                return builtins[func_name], 0.9

        elif isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
            methods = {
                "split": "list", "strip": "str", "lower": "str", "upper": "str",
                "join": "str", "keys": "dict_keys", "values": "dict_values",
                "items": "dict_items", "append": "None"
            }
            if method_name in methods:
                return methods[method_name], 0.8

        return "unknown", 0.0

    def _infer_from_binop(self, node: ast.BinOp, known: dict) -> tuple[str, float]:
        """Handle arithmetic type propagation."""
        left, l_conf = self._infer_type_from_node(node.left)
        right, r_conf = self._infer_type_from_node(node.right)
        
        if left == "int" and right == "int":
            if isinstance(node.op, ast.Div):
                return "float", max(l_conf, r_conf)
            return "int", max(l_conf, r_conf)
        elif (left == "float" and right in ("int", "float")) or (right == "float" and left in ("int", "float")):
            return "float", max(l_conf, r_conf)
        elif left == "str" and right == "str":
            return "str", max(l_conf, r_conf)
        elif left == "list" and right == "list":
            return "list", max(l_conf, r_conf)
            
        return "unknown", 0.0

    def _infer_parameter_hints(self, func_node) -> dict[str, str]:
        """
        Look at how parameters are used in the function body.
        Infer probable types from usage patterns.
        """
        hints = {}
        for arg in func_node.args.args + func_node.args.kwonlyargs:
            param_name = arg.arg
            
            for child in ast.walk(func_node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute) and isinstance(child.func.value, ast.Name):
                        if child.func.value.id == param_name:
                            meth = child.func.attr
                            if meth in ("split", "strip", "lower", "upper"):
                                hints[param_name] = "str"
                            elif meth in ("keys", "values", "items", "get"):
                                hints[param_name] = "dict"
                            elif meth in ("append", "pop"):
                                hints[param_name] = "list"
                    elif isinstance(child.func, ast.Name):
                        if child.func.id == "len" and child.args and isinstance(child.args[0], ast.Name) and child.args[0].id == param_name:
                            hints[param_name] = "list_or_str"
                elif isinstance(child, ast.Subscript):
                    if isinstance(child.value, ast.Name) and child.value.id == param_name:
                        if param_name not in hints:
                            hints[param_name] = "list_or_dict_or_str"
                elif isinstance(child, ast.For):
                    if isinstance(child.iter, ast.Name) and child.iter.id == param_name:
                        if param_name not in hints:
                            hints[param_name] = "iterable"
                elif isinstance(child, ast.Compare):
                    for op, comp in zip(child.ops, child.comparators):
                        if isinstance(op, (ast.In, ast.NotIn)) and isinstance(comp, ast.Name) and comp.id == param_name:
                            if param_name not in hints:
                                hints[param_name] = "list" 
        return hints
