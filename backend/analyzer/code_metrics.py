"""
Code Metrics Module — Advanced quality metrics beyond complexity.
Computes cyclomatic complexity, maintainability index, comment ratio, and function count.
"""
import ast
import re
import math


# ──────────────────────── AST-BASED (Python) ────────────────────────
class _MetricsVisitor(ast.NodeVisitor):
    """Walk the AST to count decision points, functions, and lines."""

    def __init__(self):
        self.decision_points = 0
        self.function_count = 0
        self.class_count = 0
        self.operators = 0
        self.operands = 0

    def visit_If(self, node):
        self.decision_points += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.decision_points += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.decision_points += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.decision_points += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # each `and` / `or` adds a decision path
        self.decision_points += len(node.values) - 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.function_count += 1
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.class_count += 1
        self.generic_visit(node)

    def visit_BinOp(self, node):
        self.operators += 1
        self.generic_visit(node)

    def visit_Compare(self, node):
        self.operators += len(node.ops)
        self.generic_visit(node)

    def visit_Name(self, node):
        self.operands += 1
        self.generic_visit(node)

    def visit_Constant(self, node):
        self.operands += 1
        self.generic_visit(node)


def _count_lines(code: str):
    """Return (total_lines, code_lines, comment_lines, blank_lines)."""
    lines = code.split("\n")
    total = len(lines)
    blank = sum(1 for l in lines if not l.strip())
    comment = sum(1 for l in lines if l.strip().startswith("#"))
    code_lines = total - blank - comment
    return total, code_lines, comment, blank


def compute_python_metrics(code: str) -> dict:
    """Full metrics for Python source using AST."""
    total, code_lines, comments, blanks = _count_lines(code)

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "total_lines": total,
            "code_lines": code_lines,
            "comment_lines": comments,
            "blank_lines": blanks,
            "cyclomatic_complexity": 1,
            "maintainability_index": 50,
            "function_count": 0,
            "class_count": 0,
            "comment_ratio": round(comments / max(total, 1) * 100, 1),
        }

    v = _MetricsVisitor()
    v.visit(tree)

    cc = v.decision_points + 1  # McCabe cyclomatic complexity

    # Halstead volume approximation
    n1 = max(v.operators, 1)
    n2 = max(v.operands, 1)
    vocabulary = n1 + n2
    length = n1 + n2
    volume = length * math.log2(max(vocabulary, 2))

    # Maintainability Index (SEI formula, capped 0-100)
    loc = max(code_lines, 1)
    mi = 171 - 5.2 * math.log(max(volume, 1)) - 0.23 * cc - 16.2 * math.log(loc)
    mi = max(0, min(100, mi))

    return {
        "total_lines": total,
        "code_lines": code_lines,
        "comment_lines": comments,
        "blank_lines": blanks,
        "cyclomatic_complexity": cc,
        "maintainability_index": round(mi, 1),
        "function_count": v.function_count,
        "class_count": v.class_count,
        "comment_ratio": round(comments / max(total, 1) * 100, 1),
    }


# ──────────────────── REGEX-BASED (Other Languages) ─────────────────
_COMMENT_PATTERNS = {
    "javascript": (r"//.*$", r"/\*[\s\S]*?\*/"),
    "java":       (r"//.*$", r"/\*[\s\S]*?\*/"),
    "c":          (r"//.*$", r"/\*[\s\S]*?\*/"),
    "cpp":        (r"//.*$", r"/\*[\s\S]*?\*/"),
}

_DECISION_KEYWORDS = {
    "javascript": [r"\bif\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"\bcatch\b", r"\b\?\b", r"&&", r"\|\|"],
    "java":       [r"\bif\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"\bcatch\b", r"\?", r"&&", r"\|\|"],
    "c":          [r"\bif\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"\?", r"&&", r"\|\|"],
    "cpp":        [r"\bif\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"\bcatch\b", r"\?", r"&&", r"\|\|"],
}

_FUNC_PATTERNS = {
    # function declarations, arrow functions, method shorthand (but NOT calls)
    "javascript": r"\bfunction\s+\w+\s*\(|\bfunction\s*\(|\b\w+\s*=\s*(?:function|\([^)]*\)\s*=>|\w+\s*=>)",
    # method declarations with return type, name, and opening paren followed by body
    "java":       r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*(?:throws\s+\w+\s*)?\{",
    "c":          r"^\s*\w[\w\s\*]*\w+\s*\([^)]*\)\s*\{",
    "cpp":        r"^\s*(?:[\w:<>*&]+\s+)+\w+\s*\([^)]*\)\s*(?:const\s*)?(?:override\s*)?\{",
}


def compute_generic_metrics(code: str, language: str) -> dict:
    """Regex-based heuristic metrics for JS/Java/C/C++."""
    lines = code.split("\n")
    total = len(lines)
    blank = sum(1 for l in lines if not l.strip())

    # Count comments
    single, multi = _COMMENT_PATTERNS.get(language, (r"//.*$", r"/\*[\s\S]*?\*/"))
    single_comments = len(re.findall(single, code, re.MULTILINE))
    multi_comments = len(re.findall(multi, code))
    comments = single_comments + multi_comments
    code_lines = total - blank - comments

    # Cyclomatic complexity
    cc = 1
    for pattern in _DECISION_KEYWORDS.get(language, []):
        cc += len(re.findall(pattern, code))

    # Function count
    func_pattern = _FUNC_PATTERNS.get(language, r"\bfunction\b")
    func_count = len(re.findall(func_pattern, code, re.MULTILINE))

    # Maintainability index (simplified)
    loc = max(code_lines, 1)
    volume = loc * math.log2(max(loc, 2))  # rough approximation
    mi = 171 - 5.2 * math.log(max(volume, 1)) - 0.23 * cc - 16.2 * math.log(loc)
    mi = max(0, min(100, mi))

    return {
        "total_lines": total,
        "code_lines": code_lines,
        "comment_lines": comments,
        "blank_lines": blank,
        "cyclomatic_complexity": cc,
        "maintainability_index": round(mi, 1),
        "function_count": func_count,
        "class_count": 0,
        "comment_ratio": round(comments / max(total, 1) * 100, 1),
    }


def compute_metrics(code: str, language: str) -> dict:
    """Dispatch to language-specific metrics computation."""
    if language == "python":
        return compute_python_metrics(code)
    return compute_generic_metrics(code, language)
