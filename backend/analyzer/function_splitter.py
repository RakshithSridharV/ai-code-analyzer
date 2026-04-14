"""
function_splitter.py
────────────────────
Walks a Python AST and runs the full analysis pipeline on every
top-level FunctionDef (or AsyncFunctionDef) individually.

Returns a list of dicts, one per function:
  {
    "name":            str,
    "time_complexity": str,
    "space_complexity": str,
    "quality_score":   int,
    "patterns":        list[str],
  }
"""

import ast

from analyzer.inference_engine import InferenceEngine
from analyzer.recursion_classifier import RecursionClassifier
from analyzer.pattern_detector import detect_patterns
from analyzer.feature_extractor import extract_features
from analyzer.ai_predictor import predict_code_quality
from analyzer.quality_score import calculate_quality_score
from analyzer.cyclomatic_analyzer import CyclomaticAnalyzer


def _is_self_recursive(func_node: ast.FunctionDef) -> bool:
    """Return True if the function calls itself by name."""
    fname = func_node.name
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == fname:
                return True
    return False


def analyze_functions(source: str) -> list[dict]:
    """
    Parse *source*, iterate over every top-level function definition,
    and run the standard analysis pipeline on each one's isolated source.

    Only top-level functions are processed (not nested ones) to avoid
    double-counting and keep results clean.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    results = []

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        # ── Isolate the function's source text ─────────────────────────
        func_src = ast.get_source_segment(source, node)
        if not func_src:
            # Fallback: reconstruct from line numbers when get_source_segment
            # is unavailable (Python < 3.8 edge-case).
            lines = source.splitlines()
            start = node.lineno - 1
            end   = getattr(node, "end_lineno", len(lines))
            func_src = "\n".join(lines[start:end])

        # ── Parse the isolated function into its own mini-tree ──────────
        try:
            func_tree = ast.parse(func_src)
        except SyntaxError:
            continue

        # ── Per-function pipeline ───────────────────────────────────────
        inference    = InferenceEngine(func_tree, func_src).analyze()
        rc           = RecursionClassifier(func_tree, func_src).classify()
        cyclomatic   = CyclomaticAnalyzer(func_tree, func_src).analyze()
        time_c       = inference["time"]
        space_c      = inference["space"]
        is_recursive = rc["is_recursive"]
        patterns = detect_patterns(
            time_complexity=time_c,
            space_complexity=space_c,
            is_recursive=is_recursive,
        )
        features      = extract_features(time_c, space_c, patterns)
        ai_prediction = predict_code_quality(features)
        quality       = calculate_quality_score(ai_prediction, features)

        results.append({
            "name":             node.name,
            "time_complexity":  time_c,
            "space_complexity": space_c,
            "quality_score":    quality,
            "patterns":         patterns,
            "cyclomatic_score": cyclomatic["score"],
            "cyclomatic_risk":  cyclomatic["risk_level"],
        })

    return results
