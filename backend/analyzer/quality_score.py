def calculate_quality_score(time_complexity, space_complexity, patterns):
    score = 100

    # ---- TIME COMPLEXITY PENALTY ----
    if "2^n" in time_complexity:
        score -= 35
    elif "n^2" in time_complexity:
        score -= 25
    elif "O(n)" in time_complexity:
        score -= 10

    # ---- SPACE COMPLEXITY PENALTY ----
    if "O(n)" in space_complexity:
        score -= 10

    # ---- PATTERN-BASED PENALTIES (AUTHORITATIVE) ----
    if "inefficient_recursion" in patterns:
        score -= 25

    if "nested_loop" in patterns:
        score -= 15

    if "extra_memory" in patterns:
        score -= 10

    # Mild penalty if recursion exists but is not inefficient
    if "recursion" in patterns and "inefficient_recursion" not in patterns:
        score -= 5

    # Clamp score
    return max(0, min(100, score))