import javalang


def analyze_java_code(code: str):
    """
    Safe Java analyzer.
    NEVER crashes Flask.
    ALWAYS returns a dict with fixed keys.
    """

    loops = 0
    recursion = False
    current_method = None

    try:
        tree = javalang.parse.parse(code)
    except Exception as e:
        # Graceful fallback — no crash
        return {
            "time_complexity": "Unknown",
            "space_complexity": "Unknown",
            "recursion": False,
            "loops": 0,
            "error": str(e)
        }

    try:
        for path, node in tree:
            # Method detection
            if isinstance(node, javalang.tree.MethodDeclaration):
                current_method = node.name

            # Loop detection
            if isinstance(
                node,
                (
                    javalang.tree.ForStatement,
                    javalang.tree.WhileStatement,
                    javalang.tree.DoStatement,
                ),
            ):
                loops += 1

            # Recursion detection
            if isinstance(node, javalang.tree.MethodInvocation):
                if node.member == current_method:
                    recursion = True

    except Exception as e:
        # AST traversal safety net
        return {
            "time_complexity": "Unknown",
            "space_complexity": "Unknown",
            "recursion": False,
            "loops": 0,
            "error": str(e)
        }

    # ---- COMPLEXITY INFERENCE ----
    if recursion:
        time_c = "O(n)"
        space_c = "O(n)"
    elif loops > 1:
        time_c = "O(n^2)"
        space_c = "O(1)"
    elif loops == 1:
        time_c = "O(n)"
        space_c = "O(1)"
    else:
        time_c = "O(1)"
        space_c = "O(1)"

    return {
        "time_complexity": time_c,
        "space_complexity": space_c,
        "recursion": recursion,
        "loops": loops
    }