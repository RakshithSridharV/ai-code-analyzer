from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import time

# Python
from analyzer.parser import parse_code
from analyzer.time_complexity import estimate_time_complexity
from analyzer.space_complexity import estimate_space_complexity
from analyzer.recursion_detector import detect_recursion, count_recursive_calls

# Shared
from analyzer.pattern_detector import detect_patterns
from analyzer.code_optimizer import get_optimized_code
from analyzer.quality_score import calculate_quality_score
from analyzer.explanations import get_detailed_explanation
from analyzer.feature_extractor import extract_features
from analyzer.ai_predictor import predict_code_quality
from analyzer.optimization_ranker import rank_optimizations
from analyzer.suggestions import get_suggestions
from analyzer.code_metrics import compute_metrics

# Multi-language (AST based)
from analyzer.language_detector import detect_language
from analyzer.c_analyzer import analyze_c_code
from analyzer.java_analyzer import analyze_java_code
from analyzer.js_analyzer import analyze_js_code
from analyzer.cpp_analyzer import analyze_cpp_code

app = Flask(__name__)
CORS(app)


# ------------------- GLOBAL ERROR HANDLER -------------------
@app.errorhandler(Exception)
def handle_exception(e):
    """Prevent uncaught exceptions from crashing the server."""
    return jsonify({
        "error": f"Internal server error: {str(e)}",
        "trace": traceback.format_exc().split("\n")[-3:]
    }), 500


@app.route("/")
def home():
    return "AI Code Analyzer Backend is running"


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": "2.0.0"})


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        t_start = time.perf_counter()
        data = request.get_json()
        code = data.get("code", "")

        if not code.strip():
            return jsonify({"error": "No code provided"})

        language = data.get("language")
        if not language or language == "auto":
            language = detect_language(code)

        # Count lines for metrics
        lines_of_code = len([l for l in code.strip().split("\n") if l.strip()])

        # ---------------- PYTHON (AST) ----------------
        if language == "python":
            tree = parse_code(code)
            if isinstance(tree, str):
                return jsonify({"error": tree})

            is_recursive = detect_recursion(tree)
            recursive_calls = count_recursive_calls(tree) if is_recursive else 0
            if is_recursive:
                time_c = "O(2^n)" if recursive_calls >= 2 else "O(n)"
            else:
                time_c = estimate_time_complexity(tree)
            space_c = estimate_space_complexity(code, is_recursive)
            loops = 0

        # ---------------- JAVASCRIPT (AST) ----------------
        elif language == "javascript":
            time_c, space_c, is_recursive, loops, recursive_calls = analyze_js_code(code)

        # ---------------- JAVA (AST) ----------------
        elif language == "java":
            java_analysis = analyze_java_code(code)
            time_c = java_analysis["time_complexity"]
            space_c = java_analysis["space_complexity"]
            is_recursive = java_analysis["recursion"]
            loops = java_analysis["loops"]
            recursive_calls = java_analysis.get("recursive_calls", 0)

        # ---------------- C (AST) ----------------
        elif language == "c":
            time_c, space_c, is_recursive, loops, recursive_calls = analyze_c_code(code)

        # ---------------- C++ (regex-based) ----------------
        elif language == "cpp":
            time_c, space_c, is_recursive, loops, recursive_calls = analyze_cpp_code(code)

        else:
            return jsonify({"error": f"Unsupported language: {language}"})

        # -------- PATTERN + AI PIPELINE --------
        patterns = detect_patterns(
            time_complexity=time_c,
            space_complexity=space_c,
            is_recursive=is_recursive
        )

        features = extract_features(time_c, space_c, patterns)
        ai_prediction = predict_code_quality(features)
        optimization_priority = rank_optimizations(patterns, ai_prediction)
        explanation = get_detailed_explanation(patterns, time_c, space_c)
        quality_score = calculate_quality_score(time_c, space_c, patterns)
        optimization = get_optimized_code(patterns, time_c, language)

        # -------- CODE METRICS --------
        metrics = compute_metrics(code, language)

        t_end = time.perf_counter()
        analysis_time_ms = round((t_end - t_start) * 1000, 1)

        return jsonify({
            "language": language,
            "analysis": {
                "time_complexity": time_c,
                "space_complexity": space_c,
                "loops": loops,
                "recursion": is_recursive,
                "lines_of_code": lines_of_code,
                "recursive_calls": recursive_calls
            },
            "metrics": metrics,
            "patterns": patterns,
            "explanation": explanation,
            "ai": {
                "prediction": ai_prediction,
                "optimization_priority": optimization_priority
            },
            "optimization": optimization,
            "suggestions": get_suggestions(patterns),
            "quality_score": quality_score,
            "analysis_time_ms": analysis_time_ms
        })

    except Exception as e:
        return jsonify({
            "error": f"Analysis failed: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True)