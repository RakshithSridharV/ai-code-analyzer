def get_suggestions(patterns):
    """
    Generate actionable optimization suggestions based on detected patterns.
    Each suggestion provides a concrete path to improvement.
    """
    suggestions = []

    if "nested_loop" in patterns:
        suggestions.append(
            "Consider restructuring nested loops using: "
            "hash maps for O(1) lookups, sorting + two pointers, "
            "or precomputed lookup tables to reduce time complexity."
        )

    if "deep_nesting" in patterns:
        suggestions.append(
            "Triple+ nested loops indicate the algorithm may need "
            "a fundamental redesign. Consider divide-and-conquer, "
            "matrix exponentiation, or mathematical shortcuts."
        )

    if "inefficient_recursion" in patterns:
        suggestions.append(
            "Apply memoization (cache results of subproblems) "
            "or convert to a bottom-up dynamic programming approach "
            "to eliminate redundant computation and achieve O(n) time."
        )

    if "linear_recursion" in patterns:
        suggestions.append(
            "This recursive function makes a single self-call per invocation. "
            "Consider converting to an iterative loop to eliminate "
            "O(n) stack overhead and prevent stack overflow on large inputs."
        )

    if "extra_memory" in patterns:
        suggestions.append(
            "Review whether all data structures are necessary. "
            "Use in-place algorithms, generators/iterators, or "
            "constant-space alternatives where possible."
        )

    if "recursion_stack" in patterns:
        suggestions.append(
            "Deep recursion risks stack overflow. Use Python's "
            "sys.setrecursionlimit() as a stopgap, or refactor to "
            "an iterative approach with an explicit stack."
        )

    if not suggestions:
        suggestions.append(
            "Code structure appears efficient — well done! "
            "No immediate optimization opportunities detected."
        )

    return suggestions
