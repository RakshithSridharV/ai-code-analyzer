from pycparser import CParser


def analyze_c_code(code):
    """
    C code analyzer with proper loop nesting depth tracking.
    Distinguishes sequential loops O(n) from nested loops O(n^k).
    """
    parser = CParser()
    max_loop_depth = 0
    loops = 0
    recursion = False
    recursive_calls = 0
    current_func = None

    try:
        ast = parser.parse(code)
    except Exception:
        return "Unknown", "Unknown", False, 0

    def walk(node, loop_depth=0):
        nonlocal loops, recursion, recursive_calls, current_func, max_loop_depth

        if not hasattr(node, "coord"):
            return

        nodetype = type(node).__name__

        if nodetype == "FuncDef":
            current_func = node.decl.name

        is_loop = nodetype in ("For", "While", "DoWhile")

        if is_loop:
            loops += 1
            loop_depth += 1
            max_loop_depth = max(max_loop_depth, loop_depth)

        if nodetype == "FuncCall":
            try:
                if node.name.name == current_func:
                    recursion = True
                    recursive_calls += 1
            except AttributeError:
                pass

        for _, child in node.children():
            walk(child, loop_depth)

    walk(ast)

    # ---- COMPLEXITY INFERENCE ----
    if recursion:
        time_c = "O(2^n)" if recursive_calls >= 2 else "O(n)"
        space_c = "O(1) + recursion stack"
    elif max_loop_depth >= 2:
        time_c = f"O(n^{max_loop_depth})"
        space_c = "O(1)"
    elif max_loop_depth == 1:
        time_c = "O(n)"
        space_c = "O(1)"
    else:
        time_c = "O(1)"
        space_c = "O(1)"

    return time_c, space_c, recursion, loops, recursive_calls