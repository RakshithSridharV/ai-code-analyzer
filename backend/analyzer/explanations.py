def get_detailed_explanation(patterns, time_complexity, space_complexity):
    explanations = []

    if "nested_loop" in patterns:
        explanations.append(
            "Nested loops were detected in the code. "
            "This causes repeated execution of inner statements for each iteration of the outer loop, "
            "resulting in quadratic or higher time complexity. "
            "Such patterns can significantly slow down performance for large input sizes."
        )

    if "inefficient_recursion" in patterns:
        explanations.append(
            "The code contains a recursive function that calls itself without optimization. "
            "This leads to repeated computation of the same subproblems, "
            "resulting in exponential time complexity. "
            "Techniques such as memoization or dynamic programming can improve performance."
        )

    if "extra_memory" in patterns:
        explanations.append(
            "Additional data structures were detected in the code, increasing memory usage. "
            "While sometimes necessary, excessive memory allocation can lead to higher space complexity. "
            "In-place operations or optimized data handling may reduce memory usage."
        )

    if "efficient_code" in patterns:
        explanations.append(
            "No major inefficiencies were detected in the code. "
            "The structure appears optimized with minimal time and space complexity."
        )

    return explanations
