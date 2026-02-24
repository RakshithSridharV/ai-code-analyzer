from pycparser import CParser

def analyze_c_code(code):
    parser = CParser()
    loops = 0
    recursion = False
    current_func = None

    try:
        ast = parser.parse(code)
    except Exception:
        return "Unknown", "Unknown", False, 0

    def walk(node):
        nonlocal loops, recursion, current_func

        if hasattr(node, "coord"):
            nodetype = type(node).__name__

            if nodetype == "FuncDef":
                current_func = node.decl.name

            if nodetype in ("For", "While", "DoWhile"):
                loops += 1

            if nodetype == "FuncCall":
                if node.name.name == current_func:
                    recursion = True

            for _, child in node.children():
                walk(child)

    walk(ast)

    if recursion:
        return "O(n)", "O(n)", True, loops
    elif loops > 1:
        return "O(n^2)", "O(1)", False, loops
    elif loops == 1:
        return "O(n)", "O(1)", False, loops
    else:
        return "O(1)", "O(1)", False, loops