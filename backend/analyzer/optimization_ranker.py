def rank_optimizations(patterns, ai_prediction):
    """
    Assign optimization priority based on AST-detected patterns
    with AI prediction as a secondary signal.
    """

    # Highest priority patterns (always critical)
    if "inefficient_recursion" in patterns:
        return "Very High"

    if "nested_loop" in patterns:
        return "Very High"

    # Medium priority issues
    if "extra_memory" in patterns:
        return "Medium"

    # Mild concern: recursion but not inefficient
    if "recursion" in patterns:
        return "Medium"

    # AI-based fallback
    if ai_prediction == "Inefficient":
        return "High"

    # Otherwise code is fine
    return "Low"