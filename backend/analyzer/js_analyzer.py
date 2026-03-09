from pyjsparser import parse


def analyze_js_code(code):
    """
    JavaScript code analyzer with proper loop nesting depth tracking.
    Distinguishes sequential loops O(n) from nested loops O(n^k).
    """
    max_loop_depth = 0
    current_loop_depth = 0
    loops = 0
    recursion = False
    recursive_calls = 0
    current_func = None

    try:
        ast = parse(code)
    except Exception:
        return "Unknown", "Unknown", False, 0

    def walk(node):
        nonlocal loops, recursion, recursive_calls, current_func
        nonlocal max_loop_depth, current_loop_depth

        if isinstance(node, dict):
            node_type = node.get("type")

            # Track current function name
            if node_type == "FunctionDeclaration":
                func_id = node.get("id")
                if func_id:
                    current_func = func_id.get("name")

            # Loop detection with depth tracking
            is_loop = node_type in (
                "ForStatement", "WhileStatement", "DoWhileStatement",
                "ForInStatement", "ForOfStatement"
            )

            if is_loop:
                loops += 1
                current_loop_depth += 1
                max_loop_depth = max(max_loop_depth, current_loop_depth)

            # Recursion detection
            if node_type == "CallExpression":
                callee = node.get("callee")
                if (
                    callee
                    and callee.get("type") == "Identifier"
                    and callee.get("name") == current_func
                ):
                    recursion = True
                    recursive_calls += 1

            # Walk children
            for value in node.values():
                walk(value)

            # Restore depth after leaving loop scope
            if is_loop:
                current_loop_depth -= 1

        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(ast)

    # ---- COMPLEXITY INFERENCE ----
    if recursion and recursive_calls >= 2:
        return "O(2^n)", "O(1) + recursion stack", True, loops, recursive_calls
    elif recursion:
        return "O(n)", "O(1) + recursion stack", True, loops, recursive_calls
    elif max_loop_depth >= 2:
        return f"O(n^{max_loop_depth})", "O(1)", False, loops, 0
    elif max_loop_depth == 1:
        return "O(n)", "O(1)", False, loops, 0
    else:
        return "O(1)", "O(1)", False, loops, 0