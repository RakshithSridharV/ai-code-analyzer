def calculate_quality_score(time_complexity, space_complexity, patterns):
    """
    Calculate a quality score (0–100) based on complexity and patterns.
    More nuanced scoring with graduated penalties.
    """
    score = 100

    # ---- TIME COMPLEXITY PENALTY ----
    if "2^n" in time_complexity:
        score -= 40
    elif "n^3" in time_complexity or "n^4" in time_complexity:
        score -= 35
    elif "n^2" in time_complexity:
        score -= 22
    elif "n log n" in time_complexity:
        score -= 12
    elif "O(n)" in time_complexity:
        score -= 8

    # ---- SPACE COMPLEXITY PENALTY ----
    if "recursion stack" in space_complexity:
        score -= 8
    if "O(n)" in space_complexity:
        score -= 6

    # ---- PATTERN-BASED PENALTIES ----
    if "inefficient_recursion" in patterns:
        score -= 20

    if "deep_nesting" in patterns:
        score -= 18

    if "nested_loop" in patterns:
        score -= 12

    if "extra_memory" in patterns:
        score -= 5

    # Mild penalty for recursion (stack usage concern)
    if "linear_recursion" in patterns:
        score -= 3

    # ---- BONUS: No issues at all ----
    if "efficient_code" in patterns:
        score = max(score, 90)  # efficiently detected code gets at least 90

    # Clamp to 0–100
    return max(0, min(100, score))