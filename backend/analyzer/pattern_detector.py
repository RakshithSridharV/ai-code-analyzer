def detect_patterns(time_complexity, space_complexity, is_recursive):
    patterns = []

    # 1️⃣ Nested loops (quadratic or worse)
    if "n^2" in time_complexity or "n^3" in time_complexity:
        patterns.append("nested_loop")

    # 2️⃣ Recursion (AST-based, always trusted)
    if is_recursive:
        patterns.append("recursion")

    # 3️⃣ Inefficient recursion (only exponential)
    if is_recursive and "2^n" in time_complexity:
        patterns.append("inefficient_recursion")

    # 4️⃣ Extra memory usage
    if "O(n)" in space_complexity:
        patterns.append("extra_memory")

    # 5️⃣ Efficient code
    if not patterns:
        patterns.append("efficient_code")

    return patterns