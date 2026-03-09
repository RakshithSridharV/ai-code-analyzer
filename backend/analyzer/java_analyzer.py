import javalang


LOOP_TYPES = (
    javalang.tree.ForStatement,
    javalang.tree.WhileStatement,
    javalang.tree.DoStatement,
)


def analyze_java_code(code: str):
    """
    Java analyzer using a recursive AST walker for accurate
    loop nesting depth and recursion call counting.
    """
    state = {
        "loops": 0,
        "max_loop_depth": 0,
        "recursion": False,
        "recursive_calls": 0,
        "current_method": None,
    }

    try:
        tree = javalang.parse.parse(code)
    except Exception as e:
        return {
            "time_complexity": "Unknown",
            "space_complexity": "Unknown",
            "recursion": False,
            "loops": 0,
            "error": str(e)
        }

    def walk_node(node, loop_depth=0):
        """Recursively walk the javalang AST tracking loop depth."""
        if node is None:
            return

        # Handle lists of nodes
        if isinstance(node, (list, tuple, set)):
            for item in node:
                walk_node(item, loop_depth)
            return

        # Skip non-AST values (strings, ints, bools, etc.)
        if not isinstance(node, javalang.ast.Node):
            return

        # --- Track method name ---
        if isinstance(node, javalang.tree.MethodDeclaration):
            state["current_method"] = node.name

        # --- Loop detection with depth tracking ---
        is_loop = isinstance(node, LOOP_TYPES)
        if is_loop:
            state["loops"] += 1
            loop_depth += 1
            state["max_loop_depth"] = max(state["max_loop_depth"], loop_depth)

        # --- Recursion detection ---
        if isinstance(node, javalang.tree.MethodInvocation):
            if node.member == state["current_method"]:
                state["recursion"] = True
                state["recursive_calls"] += 1

        # --- Walk all child attributes ---
        try:
            for child in node.children:
                walk_node(child, loop_depth)
        except Exception:
            pass  # Safety net for unusual AST shapes

    try:
        walk_node(tree)
    except Exception as e:
        return {
            "time_complexity": "Unknown",
            "space_complexity": "Unknown",
            "recursion": False,
            "loops": 0,
            "error": str(e)
        }

    # ---- COMPLEXITY INFERENCE ----
    loops = state["loops"]
    max_depth = state["max_loop_depth"]
    recursion = state["recursion"]
    recursive_calls = state["recursive_calls"]

    if recursion:
        time_c = "O(2^n)" if recursive_calls >= 2 else "O(n)"
        space_c = "O(1) + recursion stack"
    elif max_depth >= 2:
        time_c = f"O(n^{max_depth})"
        space_c = "O(1)"
    elif max_depth == 1:
        time_c = "O(n)"
        space_c = "O(1)"
    else:
        time_c = "O(1)"
        space_c = "O(1)"

    return {
        "time_complexity": time_c,
        "space_complexity": space_c,
        "recursion": recursion,
        "loops": loops,
        "recursive_calls": recursive_calls
    }