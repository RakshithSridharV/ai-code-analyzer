import pytest
from analyzer.pattern_detector import detect_patterns
from analyzer.feature_extractor import extract_features
from analyzer.quality_score import calculate_quality_score


# -------------------------
# TEST 1: Nested Loop Pattern
# -------------------------
def test_nested_loop_detection():
    time_c = "O(n^2)"
    space_c = "O(1)"
    is_recursive = False

    patterns = detect_patterns(time_c, space_c, is_recursive)

    assert "nested_loop" in patterns
    assert "efficient_code" not in patterns


# -------------------------
# TEST 2: Efficient Code Detection
# -------------------------
def test_efficient_code_detection():
    time_c = "O(n)"
    space_c = "O(1)"
    is_recursive = False

    patterns = detect_patterns(time_c, space_c, is_recursive)

    assert "efficient_code" in patterns


# -------------------------
# TEST 3: Feature Extraction Count
# -------------------------
def test_feature_extraction_length():
    time_c = "O(n^2)"
    space_c = "O(n)"
    patterns = ["nested_loop", "extra_memory"]

    features = extract_features(time_c, space_c, patterns)

    assert len(features) == 5  # must match ML model input size


# -------------------------
# TEST 4: Quality Score Range
# -------------------------
def test_quality_score_range():
    time_c = "O(n^2)"
    space_c = "O(1)"
    patterns = ["nested_loop"]

    score = calculate_quality_score(time_c, space_c, patterns)

    assert 0 <= score <= 100