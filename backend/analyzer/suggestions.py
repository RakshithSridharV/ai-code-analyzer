def get_suggestions(patterns):
    suggestions = []

    if "nested_loop" in patterns:
        suggestions.append(
            "Reduce nested iteration by restructuring logic or using a single-pass approach."
        )

    if "inefficient_recursion" in patterns:
        suggestions.append(
            "Optimize recursion using memoization or convert it to an iterative solution."
        )

    if "extra_memory" in patterns:
        suggestions.append(
            "Avoid unnecessary data structures and prefer in-place operations where possible."
        )

    if not suggestions:
        suggestions.append("Code structure appears efficient. No immediate optimization required.")

    return suggestions
