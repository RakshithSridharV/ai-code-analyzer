def detect_patterns(time_complexity, space_complexity, is_recursive):
    """
    Detect code patterns from complexity analysis results.
    Returns a list of pattern identifiers used by downstream modules.
    """
    patterns = []

    # 1. Nested loops (quadratic or worse)
    if "n^2" in time_complexity or "n^3" in time_complexity:
        patterns.append("nested_loop")

    # 2. Deep nesting (cubic or worse — triple+ nested loops)
    if "n^3" in time_complexity or "n^4" in time_complexity:
        patterns.append("deep_nesting")

    # 3. Recursion (AST-based, always trusted)
    if is_recursive:
        patterns.append("recursion")

    # 4. Inefficient recursion (exponential — branching calls)
    if is_recursive and "2^n" in time_complexity:
        patterns.append("inefficient_recursion")

    # 5. Linear recursion (single call — tail-recursion candidate)
    if is_recursive and "2^n" not in time_complexity:
        patterns.append("linear_recursion")

    # 6. Extra memory usage
    if "O(n)" in space_complexity:
        patterns.append("extra_memory")

    # 7. Recursion stack overhead
    if is_recursive and "recursion stack" in space_complexity:
        patterns.append("recursion_stack")

    # 8. Efficient code (no issues detected)
    if not patterns:
        patterns.append("efficient_code")

    return patterns