from flask import Flask, request, jsonify
from flask_cors import CORS

# Python
from analyzer.parser import parse_code
from analyzer.time_complexity import estimate_time_complexity
from analyzer.space_complexity import estimate_space_complexity
from analyzer.recursion_detector import detect_recursion

# Shared
from analyzer.pattern_detector import detect_patterns
from analyzer.code_optimizer import get_optimized_code
from analyzer.quality_score import calculate_quality_score
from analyzer.explanations import get_detailed_explanation
from analyzer.feature_extractor import extract_features
from analyzer.ai_predictor import predict_code_quality
from analyzer.optimization_ranker import rank_optimizations
from analyzer.suggestions import get_suggestions

# Multi-language (AST based)
from analyzer.language_detector import detect_language
from analyzer.c_analyzer import analyze_c_code
from analyzer.java_analyzer import analyze_java_code
from analyzer.js_analyzer import analyze_js_code

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "AI Code Analyzer Backend is running"


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    code = data.get("code", "")

    language = data.get("language")
    if not language or language == "auto":
        language = detect_language(code)

    # ---------------- PYTHON (AST) ----------------
    if language == "python":
        tree = parse_code(code)
        if isinstance(tree, str):
            return jsonify({"error": tree})

        is_recursive = detect_recursion(tree)
        time_c = "O(2^n)" if is_recursive else estimate_time_complexity(tree)
        space_c = estimate_space_complexity(code, is_recursive)
        loops = 0  # optional, python handled differently

    # ---------------- JAVASCRIPT (AST) ----------------
    elif language == "javascript":
        time_c, space_c, is_recursive, loops = analyze_js_code(code)

    # ---------------- JAVA (AST) ----------------
    elif language == "java":
        java_analysis = analyze_java_code(code)
        time_c = java_analysis["time_complexity"]
        space_c = java_analysis["space_complexity"]
        is_recursive = java_analysis["recursion"]
        loops = java_analysis["loops"]

    # ---------------- C / C++ (AST subset) ----------------
    elif language in ("c", "cpp"):
        time_c, space_c, is_recursive, loops = analyze_c_code(code)

    else:
        return jsonify({"error": f"Unsupported language: {language}"})


    # -------- PATTERN + AI PIPELINE (NO GUESSING) --------
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

    return jsonify({
        "language": language,
        "analysis": {
            "time_complexity": time_c,
            "space_complexity": space_c,
            "loops": loops,
            "recursion": is_recursive
        },
        "patterns": patterns,
        "explanation": explanation,
        "ai": {
            "prediction": ai_prediction,
            "optimization_priority": optimization_priority
        },
        "optimization": optimization,
        "suggestions": get_suggestions(patterns),
        "quality_score": quality_score
    })


if __name__ == "__main__":
    app.run(debug=True)