def extract_features(time_complexity, space_complexity, patterns):
    """
    Convert complexity + patterns into a numeric ML feature vector.
    """

    # -------- LOOP DEPTH --------
    # O(n^2), O(n^3), etc.
    if "n^" in time_complexity:
        try:
            loop_depth = int(time_complexity.split("^")[1].replace(")", ""))
        except:
            loop_depth = 2
    elif "O(n)" in time_complexity:
        loop_depth = 1
    else:
        loop_depth = 0

    # -------- RECURSION --------
    is_recursive = 1 if "inefficient_recursion" in patterns else 0

    # -------- SPACE --------
    uses_extra_memory = 1 if "O(n)" in space_complexity else 0

    # -------- TIME PENALTY --------
    if "2^n" in time_complexity:
        time_penalty = 4
    elif "n^" in time_complexity:
        time_penalty = 3
    elif "O(n)" in time_complexity:
        time_penalty = 2
    else:
        time_penalty = 1

    # -------- SPACE PENALTY --------
    space_penalty = 2 if uses_extra_memory else 1

    return [
        loop_depth,
        is_recursive,
        uses_extra_memory,
        time_penalty,
        space_penalty
    ]