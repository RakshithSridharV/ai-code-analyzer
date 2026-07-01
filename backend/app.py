from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request, jwt_required
import json
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from analyzer.parser import parse_code
from analyzer.inference_engine import InferenceEngine
from analyzer.recursion_classifier import RecursionClassifier
from analyzer.explanation_builder import ExplanationBuilder
from analyzer.data_flow_tracer import DataFlowTracer
from analyzer.anti_pattern_detector import AntiPatternDetector
from analyzer.cyclomatic_analyzer import CyclomaticAnalyzer
from analyzer.confidence_estimator import ConfidenceEstimator
from analyzer.dead_code_detector import DeadCodeDetector
from analyzer.type_inferencer import TypeInferencer
from analyzer.halstead_analyzer import HalsteadAnalyzer
from analyzer.eco_score import calculate_eco_score
from analyzer.pattern_detector import detect_patterns
from analyzer.code_optimizer import get_optimized_code
from analyzer.quality_score import calculate_quality_score
from analyzer.feature_extractor import extract_features
from analyzer.ai_predictor import predict_code_quality, model as ml_model
from analyzer.optimization_ranker import rank_optimizations
from analyzer.suggestions import get_suggestions
from analyzer.language_detector import detect_language
from analyzer.c_analyzer import analyze_c_code
from analyzer.java_analyzer import analyze_java_code
from analyzer.js_analyzer import analyze_js_code
from analyzer.cpp_analyzer import analyze_cpp_code
from analyzer.cfg_builder import CFGBuilder
from analyzer.report_builder import ReportBuilder
from ai_chat import stream_chat, get_available_models
from analyzer.function_splitter import analyze_functions
from database import init_db, save_analysis, get_history, code_hash
from auth import auth_bp
from challenges import get_all_challenges, get_challenge, grade_submission

# Ensure the DB tables exist when the server starts
init_db()

app = Flask(__name__)

# ── JWT configuration ──────────────────────────────────────────────────────────
app.config["JWT_SECRET_KEY"]       = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60 * 60 * 24 * 7  # 7 days (seconds)
jwt = JWTManager(app)

# ── CORS ───────────────────────────────────────────────────────────────────────
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "http://localhost:80",
            "https://ai-code-analyzer-git-main.vercel.app"
        ]
    }
})

# ── Security headers ───────────────────────────────────────────────────────────
csp = {
    'default-src': [
        '\'self\'',
        'https://huggingface.co',
        'https://router.huggingface.co'
    ]
}
Talisman(app, content_security_policy=csp, force_https=False)

# ── Rate limiting ──────────────────────────────────────────────────────────────
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

# ── Register blueprints ────────────────────────────────────────────────────────
app.register_blueprint(auth_bp)


# ── Global error handler ───────────────────────────────────────────────────────
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
    return jsonify({"error": "An internal server error occurred. Please try again later."}), 500


@app.route("/")
def home():
    return "AI Code Analyzer Backend is running"


@app.route("/health")
def health():
    """Health check endpoint for monitoring and orchestration."""
    return jsonify({"status": "ok", "model_loaded": ml_model is not None})


@app.route("/analyze", methods=["POST"])
@limiter.limit("30/minute")
def analyze():
    data = request.get_json()
    code = data.get("code", "")

    if len(code) > 10_000:
        return jsonify({"error": "Code too large (max 10,000 chars)"}), 400

    language = data.get("language")
    if not language or language == "auto":
        language = detect_language(code)

    logger.info("Analyzing %s code, length=%d", language, len(code))

    # ── Pre-initialise all optional fields so every branch is safe ────────────
    time_c = space_c = "Unknown"
    is_recursive = False
    loops = 0
    cyclomatic = None
    confidence = None
    dead_code = []
    type_info = {}
    halstead = {}
    data_flow = []
    anti_patterns = []
    explanation = ""
    function_breakdown = []
    recursion = {}
    non_python_patterns = []  # patterns detected by non-python analyzers

    if language == "python":
        tree = parse_code(code)
        if isinstance(tree, str):
            return jsonify({"error": tree})

        inference = InferenceEngine(tree, code).analyze()
        cyclomatic = CyclomaticAnalyzer(tree, code).analyze()
        confidence = ConfidenceEstimator(tree, code, inference).estimate()
        recursion = RecursionClassifier(tree, code).classify()
        time_c = inference["time"]
        space_c = inference["space"]
        is_recursive = recursion["is_recursive"]
        loops = 0
        dead_code = DeadCodeDetector(tree, code).detect()
        type_info = TypeInferencer(tree, code).infer()
        halstead = HalsteadAnalyzer(tree, code).analyze()
        data_flow = DataFlowTracer(tree, code, type_info).trace()
        anti_patterns = AntiPatternDetector(tree, code).detect()
        explanation = ExplanationBuilder(inference, code, "").build()
        function_breakdown = analyze_functions(code)

    elif language == "javascript":
        time_c, space_c, is_recursive, loops = analyze_js_code(code)

    elif language == "java":
        java_analysis = analyze_java_code(code)
        time_c = java_analysis["time_complexity"]
        space_c = java_analysis["space_complexity"]
        is_recursive = java_analysis["recursion"]
        loops = java_analysis["loops"]
        non_python_patterns = java_analysis.get("patterns", [])
        function_breakdown = java_analysis.get("function_breakdown", [])

    elif language == "c":
        time_c, space_c, is_recursive, loops = analyze_c_code(code)

    elif language == "cpp":
        time_c, space_c, is_recursive, loops = analyze_cpp_code(code)

    else:
        return jsonify({"error": f"Unsupported language: {language}"}), 400

    patterns = detect_patterns(
        time_complexity=time_c,
        space_complexity=space_c,
        is_recursive=is_recursive
    )
    # Merge in any language-specific patterns detected by the non-Python analyzer
    for p in non_python_patterns:
        if p not in patterns:
            patterns.append(p)

    features = extract_features(time_c, space_c, patterns)
    ai_prediction = predict_code_quality(features)
    optimization_priority = rank_optimizations(patterns, ai_prediction)
    quality_score = calculate_quality_score(ai_prediction, features)
    optimization = get_optimized_code(patterns, time_c, language)
    eco_metrics = calculate_eco_score(time_c, space_c, language)

    response = {
        "language": language,
        "analysis": {
            "time_complexity": time_c,
            "space_complexity": space_c,
            "loops": loops,
            "recursion": is_recursive,
            "eco_metrics": eco_metrics,
            "cyclomatic": cyclomatic if language == "python" else None,
            "confidence": confidence if language == "python" else None,
            "dead_code": dead_code if language == "python" else [],
            "type_info": type_info if language == "python" else {},
            "halstead": halstead if language == "python" else {},
        },
        "patterns": patterns,
        "explanation": explanation,
        "ai": {
            "prediction": ai_prediction,
            "optimization_priority": optimization_priority
        },
        "optimization": optimization,
        "suggestions": get_suggestions(patterns),
        "quality_score": quality_score,
        "recursion_detail": recursion if language == "python" else {},
        "data_flow": data_flow if language == "python" else [],
        "anti_patterns": anti_patterns if language == "python" else [],
        "functions": function_breakdown,
    }

    # ── Persist to history (best-effort) ──────────────────────────────────────
    try:
        # Extract user_id from JWT if present (optional auth)
        current_user_id = None
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                current_user_id = int(identity)
        except Exception:
            pass

        eco_score_val = None
        if eco_metrics and isinstance(eco_metrics, dict):
            eco_score_val = eco_metrics.get("eco_score_100")

        cyclomatic_score_val = None
        if cyclomatic and isinstance(cyclomatic, dict):
            cyclomatic_score_val = cyclomatic.get("score")

        halstead_bugs_val = None
        if halstead and isinstance(halstead, dict):
            halstead_bugs_val = halstead.get("bugs_estimated")

        save_analysis({
            "language":         language,
            "time_complexity":  time_c,
            "space_complexity": space_c,
            "quality_score":    quality_score,
            "eco_score":        eco_score_val,
            "code_hash":        code_hash(code),
            "user_id":          current_user_id,
            "cyclomatic_score": cyclomatic_score_val,
            "halstead_bugs":    halstead_bugs_val,
        })
    except Exception as db_err:
        logger.warning("Failed to persist analysis: %s", db_err)

    return jsonify(response)


@app.route("/cfg", methods=["POST"])
@limiter.limit("20/minute")
def cfg():
    """
    Build and return a Control Flow Graph for Python code.
    Request body: {"code": str, "language": str}
    Returns: CFG dict or error
    """
    data = request.get_json()
    code = data.get("code", "")

    if len(code) > 10_000:
        return jsonify({"error": "Code too large"}), 400

    language = data.get("language", "python")
    if language != "python":
        return jsonify({"error": "CFG is only supported for Python"}), 400

    tree = parse_code(code)
    if isinstance(tree, str):
        return jsonify({"error": tree}), 400

    cfg_result = CFGBuilder(tree, code).build()
    return jsonify(cfg_result)


@app.route("/report", methods=["POST"])
@limiter.limit("10/minute")
def report():
    """
    Generate a plain-text analysis report.
    Request body: {"analysis_result": dict, "code": str}
    Returns: {"report": str}
    """
    data = request.get_json()
    analysis_result = data.get("analysis_result", {})
    code = data.get("code", "")
    report_text = ReportBuilder(analysis_result, code).build()
    return jsonify({"report": report_text})


@app.route("/history", methods=["GET"])
@jwt_required()
def history():
    """Return the last 50 analysis records for the authenticated user."""
    try:
        user_id = int(get_jwt_identity())
        limit = min(int(request.args.get("limit", 50)), 100)
        return jsonify({"history": get_history(limit, user_id=user_id)})
    except Exception as e:
        logger.error(f"Error in /history: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch history"}), 500


@app.route("/challenges", methods=["GET"])
def challenges_list():
    """Return all challenges (without test_cases) for the challenge picker."""
    return jsonify({"challenges": get_all_challenges()})


@app.route("/challenges/<int:challenge_id>/submit", methods=["POST"])
@limiter.limit("20/minute")
def challenges_submit(challenge_id: int):
    """
    Grade a challenge submission.

    Request body: {"code": str}
    Response: grading dict from grade_submission()
    """
    challenge = get_challenge(challenge_id)
    if challenge is None:
        return jsonify({"error": f"Challenge {challenge_id} not found."}), 404

    data = request.get_json(silent=True) or {}
    code = data.get("code", "").strip()

    if not code:
        return jsonify({"error": "No code submitted."}), 400

    if len(code) > 10_000:
        return jsonify({"error": "Code too large (max 10,000 chars)."}), 400

    # ── ASTra complexity analysis (Python only) ────────────────────────────────
    achieved_complexity = "Unknown"
    try:
        from analyzer.parser import parse_code as _parse
        tree = _parse(code)
        if not isinstance(tree, str):                  # str = parse error
            inference = InferenceEngine(tree, code).analyze()
            achieved_complexity = inference.get("time", "Unknown")
    except Exception as analysis_err:
        logger.warning("Challenge analysis error: %s", analysis_err)

    # ── Grade the submission ───────────────────────────────────────────────────
    try:
        result = grade_submission(challenge_id, code, achieved_complexity)
        return jsonify(result)
    except Exception as e:
        logger.error("Challenge grading error: %s", e, exc_info=True)
        return jsonify({"error": f"Grading failed: {e}"}), 500


@app.route("/chat", methods=["POST"])
def chat():
    """Stream AI chat responses via Server-Sent Events."""
    data = request.get_json()
    message = data.get("message", "")
    history = data.get("history", [])
    model = data.get("model", None)
    analysis_context = data.get("analysis_context", None)
    system_instruction = data.get("system_instruction", None)

    if not message.strip():
        return jsonify({"error": "Message cannot be empty"}), 400

    def generate():
        for chunk in stream_chat(message, history, model, analysis_context, system_instruction):
            payload = json.dumps({"content": chunk})
            yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.route("/chat/models", methods=["GET"])
def chat_models():
    """Return available AI models."""
    return jsonify({"models": get_available_models()})


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", debug=debug_mode)