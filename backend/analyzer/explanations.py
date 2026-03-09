def get_detailed_explanation(patterns, time_complexity, space_complexity):
    """
    Generate detailed, educational explanations based on detected patterns.
    Each explanation helps the developer understand WHY the pattern is a concern.
    """
    explanations = []

    if "nested_loop" in patterns:
        explanations.append(
            "Nested loops were detected in the code. "
            "This causes repeated execution of inner statements for each iteration of the outer loop, "
            "resulting in quadratic or higher time complexity. "
            "For an input of size 1000, O(n²) means ~1,000,000 operations. "
            "Consider using hash maps, sorting, or algebraic techniques to reduce loop nesting."
        )

    if "deep_nesting" in patterns:
        explanations.append(
            "Deeply nested loops (3+ levels) were detected. "
            "This results in cubic or higher time complexity, which becomes "
            "extremely slow for inputs beyond a few hundred elements. "
            "At n=100, O(n³) means 1,000,000 operations. "
            "Restructure the algorithm to flatten nesting, or use divide-and-conquer approaches."
        )

    if "inefficient_recursion" in patterns:
        explanations.append(
            "The code contains a recursive function with multiple self-calls (branching recursion). "
            "This causes repeated computation of the same subproblems — for example, "
            "fib(5) recalculates fib(3) multiple times. "
            "This results in exponential O(2^n) time complexity. "
            "Techniques such as memoization, dynamic programming, or iterative conversion "
            "can reduce this to linear O(n) time."
        )

    if "linear_recursion" in patterns:
        explanations.append(
            "The code uses linear recursion (one self-call per invocation). "
            "While this gives O(n) time complexity, it still uses O(n) stack space. "
            "This is a good candidate for tail-call optimization or conversion "
            "to an iterative loop, which would reduce space complexity to O(1)."
        )

    if "extra_memory" in patterns and "recursion_stack" not in patterns:
        explanations.append(
            "Additional data structures (lists, dictionaries, sets) were detected, "
            "causing O(n) space complexity. While sometimes necessary, "
            "consider whether in-place operations or streaming approaches "
            "could reduce memory usage without sacrificing readability."
        )

    if "recursion_stack" in patterns:
        explanations.append(
            "Recursive calls create stack frames proportional to the recursion depth. "
            "For deep recursion, this can cause stack overflow errors. "
            "Converting to an iterative approach with an explicit stack or loop "
            "can prevent this issue."
        )

    if "efficient_code" in patterns:
        explanations.append(
            "No major inefficiencies were detected. "
            "The code structure appears well-optimized with minimal time and space complexity. "
            "Great job — the algorithm is efficient for its purpose."
        )

    return explanations
